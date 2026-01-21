from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from dotenv import load_dotenv
from src.auth.dependencies import get_current_user
from src.db.main import get_db
from src.db.models import User, Wallet
from src.schema.schemas import (
    UserCreate, UserLogin,
)
from src.auth.auth import verify_password, get_password_hash, create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES

load_dotenv()
class AuthService:
    async def register(self, user_data: UserCreate, db: AsyncSession):
        # Check if user exists
        result = await db.execute(
            select(User).where((User.email == user_data.email) | (User.phone == user_data.phone))
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email or phone already registered")

        # Create user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            phone=user_data.phone,
            name=user_data.name,
            hashed_password=hashed_password,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Create wallet for user
        wallet = Wallet(user_uid=new_user.uid)
        db.add(wallet)
        await db.commit()

        return new_user

    async def login(self, user_data: UserLogin, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == user_data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.uid)}, expires_delta=access_token_expires
        )

        return access_token

    async def get_me(self, current_user: User = Depends(get_current_user)):
        return current_user