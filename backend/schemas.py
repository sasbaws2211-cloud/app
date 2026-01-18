from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    name: str
    password: str
    
    @field_validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    phone: str
    name: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    amount: float = Field(gt=0)
    phone_number: str
    provider: str = Field(description="MTN, Vodafone, or AirtelTigo")

class WithdrawRequest(BaseModel):
    amount: float = Field(gt=0)
    phone_number: str
    provider: str

class TransferRequest(BaseModel):
    to_user_id: int
    amount: float = Field(gt=0)
    description: Optional[str] = None

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    contribution_amount: float = Field(default=0.0, ge=0)
    contribution_frequency: str = "monthly"

class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    contribution_amount: float
    contribution_frequency: str
    invite_code: str
    created_by: int
    created_at: datetime
    member_count: Optional[int] = None
    wallet_balance: Optional[float] = None
    
    class Config:
        from_attributes = True

class ContributionRequest(BaseModel):
    group_id: int
    amount: float = Field(gt=0)

class DisbursementRequest(BaseModel):
    group_id: int
    to_user_id: int
    amount: float = Field(gt=0)
    description: str

class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: float
    status: str
    description: Optional[str]
    from_user_id: Optional[int]
    to_user_id: Optional[int]
    group_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    group_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    group_id: int
    sender_id: int
    sender_name: Optional[str]
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True