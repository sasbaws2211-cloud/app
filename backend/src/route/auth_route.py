from fastapi import Depends, status,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv 
from src.service.auth_service import AuthService
from src.auth.dependencies import get_current_user,AccessTokenBearer
from src.db.main import get_db
from src.db.models import User
from src.schema.schemas import (
    UserCreate, UserLogin, UserResponse, Token
)
load_dotenv() 


auth_router = APIRouter()
auth_service = AuthService()
acccess_token_bearer = AccessTokenBearer() 


@auth_router.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession= Depends(get_db) ):
    # Check if user exists
    new_user = await auth_service.register(user_data,db)
    return new_user

@auth_router.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    access_token = await auth_service.login(user_data,db)
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user