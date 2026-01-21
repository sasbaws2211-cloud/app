from fastapi import Depends, HTTPException,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from src.auth.dependencies import get_current_user,AccessTokenBearer
from src.db.main import get_db
from src.db.models import User, Wallet,Transaction,TransactionStatus, TransactionType
from src.schema.schemas import ( WalletResponse,
    DepositRequest, WithdrawRequest, TransferRequest,
    TransactionResponse
)
from fastapi import Request 
from src.service.wallet_service import WalletService 
from src.service.hubtel_service import HubtelService 
from src.service.hubtel_service import verify_hubtel_signature 
from src.service.hubtel_audit import log_hubtel_event
from decimal import Decimal 
import logging  

logger = logging.getLogger(__name__)

load_dotenv() 

wallet_router = APIRouter()
wallet_service = WalletService() 
hubtel_service = HubtelService()
acccess_token_bearer = AccessTokenBearer() 

@wallet_router.get("/api/wallet", response_model=WalletResponse)
async def get_wallet(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    wallet = await wallet_service.get_wallet(current_user,db)
    return wallet

@wallet_router.post("/api/wallet/deposit", response_model=TransactionResponse)
async def deposit_money(
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transaction = await wallet_service.deposit_money(deposit_data,current_user,db)

    return transaction



@wallet_router.post("/api/wallet/hubtel/webhook")
async def hubtel_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()
    payload = await request.json()

    secret = os.getenv("HUBTEL_WEBHOOK_SECRET")
    signature = request.headers.get("X-Hubtel-Signature")

    # ---------------------------------------------------
    # 1. Verify signature (but DO NOT reject yet)
    # ---------------------------------------------------
    signature_valid = False
    if secret and signature:
        signature_valid = verify_hubtel_signature(body, signature, secret)

    data = payload.get("Data") or payload

    external_id = (
        data.get("ExternalId")
        or data.get("TransactionId")
        or data.get("ClientReference")
    )
    transaction_id = data.get("TransactionId")
    status_str = data.get("Status")
    amount = Decimal(str(data.get("Amount", "0")))

    # ---------------------------------------------------
    # 2. AUDIT LOG (ALWAYS)
    # ---------------------------------------------------
    await log_hubtel_event(
        db,
        payload=payload,
        signature_valid=signature_valid,
        external_id=external_id,
        transaction_id=transaction_id,
        status=status_str,
    )

    # ---------------------------------------------------
    # 3. Enforce signature AFTER logging
    # ---------------------------------------------------
    if secret:
        if not signature:
            await db.commit()
            raise HTTPException(400, "Missing Hubtel signature")

        if not signature_valid:
            await db.commit()
            raise HTTPException(400, "Invalid Hubtel signature")

    if not external_id or not status_str:
        await db.commit()
        return {"success": False, "reason": "missing required fields"}

    status_map = {
        "completed": TransactionStatus.COMPLETED,
        "success": TransactionStatus.COMPLETED,
        "failed": TransactionStatus.FAILED,
        "pending": TransactionStatus.PENDING,
    }

    new_status = status_map.get(status_str.lower(), TransactionStatus.PENDING)

    tx = (
        await db.execute(
            select(Transaction)
            .where(Transaction.external_reference == external_id)
        )
    ).scalar_one_or_none()

    if not tx:
        await db.commit()
        return {"success": False, "reason": "transaction not found"}

    # ---------------------------------------------------
    # 4. Amount safety check
    # ---------------------------------------------------
    if tx.amount != amount:
        logger.critical(
            "Amount mismatch for tx %s: expected %s, got %s",
            external_id, tx.amount, amount
        )
        await db.commit()
        raise HTTPException(400, "Amount mismatch")

    # Idempotency
    if tx.status == new_status:
        await db.commit()
        return {"success": True, "message": "no change"}

    # ---------------------------------------------------
    # 5. Wallet settlement logic (UNCHANGED)
    # ---------------------------------------------------
    tx.status = new_status
    tx.updated_at = datetime.now(timezone.utc)

    if new_status == TransactionStatus.COMPLETED:
        tx.completed_at = datetime.now(timezone.utc)

        if tx.transaction_type == TransactionType.DEPOSIT:
            wallet = (
                await db.execute(
                    select(Wallet).where(Wallet.user_uid == tx.to_user_uid)
                )
            ).scalar_one()
            wallet.balance += tx.amount

        elif tx.transaction_type == TransactionType.WITHDRAWAL:
            wallet = (
                await db.execute(
                    select(Wallet).where(Wallet.user_uid == tx.from_user_uid)
                )
            ).scalar_one()
            wallet.locked_balance -= tx.amount

    elif new_status == TransactionStatus.FAILED:
        if tx.transaction_type == TransactionType.WITHDRAWAL:
            wallet = (
                await db.execute(
                    select(Wallet).where(Wallet.user_uid == tx.from_user_uid)
                )
            ).scalar_one()
            wallet.balance += tx.amount
            wallet.locked_balance -= tx.amount

    # ---------------------------------------------------
    # 6. Mark audit event as processed
    # ---------------------------------------------------
    await db.execute(
        """
        UPDATE hubtel_events
        SET processed = true
        WHERE transaction_id = :tx_id
          AND processed = false
        """,
        {"tx_id": transaction_id},
    )

    await db.commit()
    return {"success": True}




@wallet_router.post("/api/wallet/withdraw", response_model=TransactionResponse)
async def withdraw_money(
    withdraw_data: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transaction = await wallet_service.withdraw_money(withdraw_data,current_user,db)
    return transaction


@wallet_router.post("/api/wallet/transfer", response_model=TransactionResponse)
async def transfer_money(
    transfer_data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transaction = await wallet_service.transfer_money(transfer_data,current_user,db)
    
    return transaction