from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import  datetime, timezone
from dotenv import load_dotenv
from src.db.main import get_db
from src.db.models import User, Wallet,Transaction,TransactionStatus, TransactionType
from src.schema.schemas import (DepositRequest, WithdrawRequest, TransferRequest)
from src.utils import format_phone_number
from src.service.hubtel_service import HubtelService
from src.auth.dependencies import get_current_user
load_dotenv() 

hubtel_service = HubtelService()
class WalletService:

 async def get_wallet(self,current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_uid == current_user.uid))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return wallet


 async def deposit_money( 
    self,
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    phone = format_phone_number(deposit_data.phone_number)

    hubtel_response = await hubtel_service.initiate_deposit(
        phone,
        deposit_data.amount,
        deposit_data.provider
    )

    transaction = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=deposit_data.amount,
        status=TransactionStatus.PENDING,   # ALWAYS pending
        to_user_uid=current_user.uid,
        phone_number=phone,
        mobile_money_provider=deposit_data.provider,
        external_reference=hubtel_response["external_id"],
        description=f"Deposit via {deposit_data.provider}"
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction



 async def withdraw_money( 
    self,
    withdraw_data: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Wallet).where(Wallet.user_uid == current_user.uid))
    wallet = result.scalar_one_or_none()

    if not wallet or wallet.balance < withdraw_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    phone = format_phone_number(withdraw_data.phone_number)

    hubtel_response = await hubtel_service.initiate_withdrawal(
        phone,
        withdraw_data.amount,
        withdraw_data.provider
    )

    async with db.begin():  # ATOMIC
        transaction = Transaction(
            transaction_type=TransactionType.WITHDRAWAL,
            amount=withdraw_data.amount,
            status=TransactionStatus.PENDING,
            from_user_uid=current_user.uid,
            phone_number=phone,
            mobile_money_provider=withdraw_data.provider,
            external_reference=hubtel_response["external_id"],
            description=f"Withdrawal to {withdraw_data.provider}"
        )

        wallet.balance -= withdraw_data.amount
        wallet.locked_balance += withdraw_data.amount

        db.add(transaction)

    await db.refresh(transaction)
    return transaction



 async def transfer_money( 
    self,
    transfer_data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get sender wallet
    result = await db.execute(select(Wallet).where(Wallet.user_uid == current_user.uid))
    sender_wallet = result.scalar_one_or_none()
    
    if not sender_wallet or sender_wallet.balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Get receiver wallet
    result = await db.execute(select(Wallet).where(Wallet.user_uid == transfer_data.to_user_uid))
    receiver_wallet = result.scalar_one_or_none()
    
    if not receiver_wallet:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Create transaction
    transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=transfer_data.amount,
        status=TransactionStatus.COMPLETED,
        from_user_uid=current_user.uid,
        to_user_uid=transfer_data.to_user_uid,
        description=transfer_data.description or "Wallet transfer",
        completed_at=datetime.now(timezone.utc)
    )
    
    db.add(transaction)
    
    # Update balances
    sender_wallet.balance -= transfer_data.amount
    receiver_wallet.balance += transfer_data.amount
    sender_wallet.updated_at = datetime.now(timezone.utc)
    receiver_wallet.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction