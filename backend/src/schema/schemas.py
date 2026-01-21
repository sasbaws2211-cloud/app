import uuid
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
    uid: uuid.UUID
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
    uid: uuid.UUID
    user_uid: uuid.UUID
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
    to_user_uid: uuid.UUID
    amount: float = Field(gt=0)
    description: Optional[str] = None

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    contribution_amount: float = Field(default=0.0, ge=0)
    contribution_frequency: str = "monthly"


class GroupMemberResponse(BaseModel):
    uid: uuid.UUID
    user_uid: uuid.UUID
    name: str
    is_admin: bool

    class Config:
        from_attributes = True

class GroupResponse(BaseModel):
    uid: uuid.UUID
    name: str
    description: Optional[str]
    contribution_amount: float
    contribution_frequency: str
    invite_code: str
    created_by: uuid.UUID
    member_count: Optional[int] = None
    wallet_balance: Optional[float] = None
    members: Optional[List[GroupMemberResponse]] = None
    policies: Optional[str] = None
    
    class Config:
        from_attributes = True

class ContributionRequest(BaseModel):
    group_uid: str
    amount: float = Field(gt=0)

class DisbursementRequest(BaseModel):
    group_uid: uuid.UUID
    to_user_uid: uuid.UUID
    amount: float = Field(gt=0)
    description: str


class PoliciesUpdate(BaseModel):
    policies: str

class TransactionResponse(BaseModel):
    uid: uuid.UUID
    transaction_type: str
    amount: float
    status: str
    description: Optional[str]
    from_user_uid: Optional[uuid.UUID]
    to_user_uid: Optional[uuid.UUID]
    group_uid: Optional[uuid.UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    group_uid: uuid.UUID
    content: str

class MessageResponse(BaseModel):
    uid: uuid.UUID
    group_uid: uuid.UUID
    sender_uid: uuid.UUID
    sender_name: Optional[str]
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True