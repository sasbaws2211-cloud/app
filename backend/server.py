from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv
import json

from database import get_db, init_db
from models import User, Wallet, Group, GroupMember, GroupWallet, Transaction, Message, TransactionStatus, TransactionType
from schemas import (
    UserCreate, UserLogin, UserResponse, Token, WalletResponse,
    DepositRequest, WithdrawRequest, TransferRequest,
    GroupCreate, GroupResponse, ContributionRequest, DisbursementRequest,
    TransactionResponse, MessageCreate, MessageResponse
)
from auth import verify_password, get_password_hash, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from utils import generate_invite_code, format_phone_number, validate_mobile_money_provider
from hubtel_service import MockHubtelService

load_dotenv()

app = FastAPI(title="SusuFlow API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
hubtel_service = MockHubtelService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}  # group_id -> list of websockets
    
    async def connect(self, websocket: WebSocket, group_id: int):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, group_id: int):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
    
    async def broadcast(self, message: str, group_id: int):
        if group_id in self.active_connections:
            for connection in self.active_connections[group_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

# Database initialization
@app.on_event("startup")
async def startup_event():
    await init_db()
    print("Database tables created successfully!")

# Auth endpoints
@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(
        (User.email == user_data.email) | (User.phone == user_data.phone)
    ))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or phone already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        phone=user_data.phone,
        name=user_data.name,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create wallet for user
    wallet = Wallet(user_id=new_user.id)
    db.add(wallet)
    await db.commit()
    
    return new_user

@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Wallet endpoints
@app.get("/api/wallet", response_model=WalletResponse)
async def get_wallet(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return wallet

@app.post("/api/wallet/deposit", response_model=TransactionResponse)
async def deposit_money(
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validate provider
    if not validate_mobile_money_provider(deposit_data.provider):
        raise HTTPException(status_code=400, detail="Invalid mobile money provider")
    
    # Format phone number
    phone = format_phone_number(deposit_data.phone_number)
    
    # Initiate deposit with Hubtel
    hubtel_response = await hubtel_service.initiate_deposit(
        phone, deposit_data.amount, deposit_data.provider
    )
    
    # Create transaction record
    transaction = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=deposit_data.amount,
        status=TransactionStatus.COMPLETED if hubtel_response["status"] == "success" else TransactionStatus.PENDING,
        to_user_id=current_user.id,
        phone_number=phone,
        mobile_money_provider=deposit_data.provider,
        external_reference=hubtel_response["transaction_id"],
        description=f"Deposit via {deposit_data.provider}"
    )
    
    db.add(transaction)
    
    # Update wallet balance if successful
    if hubtel_response["status"] == "success":
        result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
        wallet = result.scalar_one()
        wallet.balance += deposit_data.amount
        wallet.updated_at = datetime.now(timezone.utc)
        transaction.completed_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction

@app.post("/api/wallet/withdraw", response_model=TransactionResponse)
async def withdraw_money(
    withdraw_data: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get wallet
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    
    if not wallet or wallet.balance < withdraw_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Validate provider
    if not validate_mobile_money_provider(withdraw_data.provider):
        raise HTTPException(status_code=400, detail="Invalid mobile money provider")
    
    # Format phone number
    phone = format_phone_number(withdraw_data.phone_number)
    
    # Initiate withdrawal with Hubtel
    hubtel_response = await hubtel_service.initiate_withdrawal(
        phone, withdraw_data.amount, withdraw_data.provider
    )
    
    # Create transaction and update wallet
    transaction = Transaction(
        transaction_type=TransactionType.WITHDRAWAL,
        amount=withdraw_data.amount,
        status=TransactionStatus.COMPLETED if hubtel_response["status"] == "success" else TransactionStatus.PENDING,
        from_user_id=current_user.id,
        phone_number=phone,
        mobile_money_provider=withdraw_data.provider,
        external_reference=hubtel_response["transaction_id"],
        description=f"Withdrawal to {withdraw_data.provider}"
    )
    
    db.add(transaction)
    
    if hubtel_response["status"] == "success":
        wallet.balance -= withdraw_data.amount
        wallet.updated_at = datetime.now(timezone.utc)
        transaction.completed_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction

@app.post("/api/wallet/transfer", response_model=TransactionResponse)
async def transfer_money(
    transfer_data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get sender wallet
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    sender_wallet = result.scalar_one_or_none()
    
    if not sender_wallet or sender_wallet.balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Get receiver wallet
    result = await db.execute(select(Wallet).where(Wallet.user_id == transfer_data.to_user_id))
    receiver_wallet = result.scalar_one_or_none()
    
    if not receiver_wallet:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Create transaction
    transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=transfer_data.amount,
        status=TransactionStatus.COMPLETED,
        from_user_id=current_user.id,
        to_user_id=transfer_data.to_user_id,
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

# Group endpoints
@app.post("/api/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Generate unique invite code
    invite_code = generate_invite_code()
    
    # Create group
    group = Group(
        name=group_data.name,
        description=group_data.description,
        contribution_amount=group_data.contribution_amount,
        contribution_frequency=group_data.contribution_frequency,
        invite_code=invite_code,
        created_by=current_user.id
    )
    
    db.add(group)
    await db.flush()
    
    # Add creator as admin member
    member = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        is_admin=True
    )
    
    db.add(member)
    
    # Create group wallet
    group_wallet = GroupWallet(group_id=group.id)
    db.add(group_wallet)
    
    await db.commit()
    await db.refresh(group)
    
    return group

@app.get("/api/groups", response_model=List[GroupResponse])
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Group, GroupWallet, func.count(GroupMember.id).label('member_count'))
        .join(GroupMember, Group.id == GroupMember.group_id)
        .join(GroupWallet, Group.id == GroupWallet.group_id)
        .where(GroupMember.user_id == current_user.id)
        .group_by(Group.id, GroupWallet.id)
    )
    
    groups_data = result.all()
    
    groups = []
    for group, wallet, member_count in groups_data:
        group_dict = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "contribution_amount": group.contribution_amount,
            "contribution_frequency": group.contribution_frequency,
            "invite_code": group.invite_code,
            "created_by": group.created_by,
            "created_at": group.created_at,
            "member_count": member_count,
            "wallet_balance": wallet.balance
        }
        groups.append(GroupResponse(**group_dict))
    
    return groups

@app.get("/api/groups/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if user is member
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return group

@app.post("/api/groups/join/{invite_code}")
async def join_group(
    invite_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Find group
    result = await db.execute(select(Group).where(Group.invite_code == invite_code))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    
    # Check if already member
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group.id, GroupMember.user_id == current_user.id)
        )
    )
    existing_member = result.scalar_one_or_none()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="Already a member")
    
    # Add member
    member = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        is_admin=False
    )
    
    db.add(member)
    await db.commit()
    
    return {"message": "Successfully joined group", "group_id": group.id}

@app.post("/api/groups/{group_id}/contribute", response_model=TransactionResponse)
async def contribute_to_group(
    group_id: int,
    contribution_data: ContributionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check membership
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Get user wallet
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    user_wallet = result.scalar_one_or_none()
    
    if not user_wallet or user_wallet.balance < contribution_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Get group wallet
    result = await db.execute(select(GroupWallet).where(GroupWallet.group_id == group_id))
    group_wallet = result.scalar_one_or_none()
    
    # Create transaction
    transaction = Transaction(
        transaction_type=TransactionType.CONTRIBUTION,
        amount=contribution_data.amount,
        status=TransactionStatus.COMPLETED,
        from_user_id=current_user.id,
        group_id=group_id,
        description="Group contribution",
        completed_at=datetime.now(timezone.utc)
    )
    
    db.add(transaction)
    
    # Update balances
    user_wallet.balance -= contribution_data.amount
    group_wallet.balance += contribution_data.amount
    user_wallet.updated_at = datetime.now(timezone.utc)
    group_wallet.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction

@app.post("/api/groups/{group_id}/disburse", response_model=TransactionResponse)
async def disburse_from_group(
    group_id: int,
    disbursement_data: DisbursementRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if user is admin
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id,
                GroupMember.is_admin == True
            )
        )
    )
    admin_membership = result.scalar_one_or_none()
    
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Only admins can disburse funds")
    
    # Get group wallet
    result = await db.execute(select(GroupWallet).where(GroupWallet.group_id == group_id))
    group_wallet = result.scalar_one_or_none()
    
    if not group_wallet or group_wallet.balance < disbursement_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient group balance")
    
    # Get recipient wallet
    result = await db.execute(select(Wallet).where(Wallet.user_id == disbursement_data.to_user_id))
    recipient_wallet = result.scalar_one_or_none()
    
    if not recipient_wallet:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Create transaction
    transaction = Transaction(
        transaction_type=TransactionType.DISBURSEMENT,
        amount=disbursement_data.amount,
        status=TransactionStatus.COMPLETED,
        to_user_id=disbursement_data.to_user_id,
        group_id=group_id,
        description=disbursement_data.description,
        completed_at=datetime.now(timezone.utc)
    )
    
    db.add(transaction)
    
    # Update balances
    group_wallet.balance -= disbursement_data.amount
    recipient_wallet.balance += disbursement_data.amount
    group_wallet.updated_at = datetime.now(timezone.utc)
    recipient_wallet.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction

@app.get("/api/groups/{group_id}/transactions", response_model=List[TransactionResponse])
async def get_group_transactions(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check membership
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    result = await db.execute(
        select(Transaction)
        .where(Transaction.group_id == group_id)
        .order_by(Transaction.created_at.desc())
    )
    transactions = result.scalars().all()
    
    return transactions

@app.get("/api/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Transaction)
        .where(
            (Transaction.from_user_id == current_user.id) |
            (Transaction.to_user_id == current_user.id)
        )
        .order_by(Transaction.created_at.desc())
        .limit(50)
    )
    transactions = result.scalars().all()
    
    return transactions

# Chat/Messages endpoints
@app.get("/api/groups/{group_id}/messages", response_model=List[MessageResponse])
async def get_group_messages(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check membership
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    result = await db.execute(
        select(Message, User.name)
        .join(User, Message.sender_id == User.id)
        .where(Message.group_id == group_id)
        .order_by(Message.created_at.asc())
        .limit(100)
    )
    
    messages_data = result.all()
    
    messages = []
    for message, sender_name in messages_data:
        msg_dict = {
            "id": message.id,
            "group_id": message.group_id,
            "sender_id": message.sender_id,
            "sender_name": sender_name,
            "content": message.content,
            "created_at": message.created_at
        }
        messages.append(MessageResponse(**msg_dict))
    
    return messages

# WebSocket endpoint for real-time chat
@app.websocket("/api/ws/chat/{group_id}")
async def websocket_chat(websocket: WebSocket, group_id: int, token: str):
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008)
        return
    
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008)
        return
    
    # Get database session
    async for db in get_db():
        # Check membership
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            await websocket.close(code=1008)
            return
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        
        await manager.connect(websocket, group_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Save message to database
                message = Message(
                    group_id=group_id,
                    sender_id=user_id,
                    content=message_data["content"]
                )
                
                db.add(message)
                await db.commit()
                await db.refresh(message)
                
                # Broadcast to all group members
                broadcast_data = {
                    "id": message.id,
                    "sender_id": user_id,
                    "sender_name": user.name,
                    "content": message.content,
                    "created_at": message.created_at.isoformat()
                }
                
                await manager.broadcast(json.dumps(broadcast_data), group_id)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, group_id)
        except Exception as e:
            print(f"WebSocket error: {e}")
            manager.disconnect(websocket, group_id)

@app.get("/api/")
async def root():
    return {"message": "SusuFlow API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
