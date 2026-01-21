from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timezone
import enum
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Relationship ,Column
from sqlalchemy import Column as SAColumn, String as SAString, Enum as SAEnum 
from sqlalchemy import JSON, Boolean, Index 
from sqlalchemy.sql import func 



class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    CONTRIBUTION = "contribution"
    DISBURSEMENT = "disbursement"


class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


def now_utc():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    email: str = Field(sa_column=SAColumn(SAString, unique=True, index=True, nullable=False))
    phone: str = Field(sa_column=SAColumn(SAString, unique=True, index=True, nullable=False))
    name: str
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER, sa_column=SAColumn(SAEnum(UserRole)))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))

    wallet: Optional["Wallet"] = Relationship(back_populates="user")
    group_members: List["GroupMember"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="sender")


class Wallet(SQLModel, table=True):
    __tablename__ = "wallets"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    user_uid:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.uid",default=None)
    balance: float = Field(default=0.0)
    locked_balance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))
    updated_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))

    user: Optional[User] = Relationship(back_populates="wallet")


class Group(SQLModel, table=True):
    __tablename__ = "groups"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str
    description: Optional[str] = None
    contribution_amount: float = Field(default=0.0)
    contribution_frequency: str = Field(default="monthly")
    invite_code: Optional[str] = Field(default=None, sa_column=SAColumn(SAString, unique=True, index=True))
    created_by: Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.uid",default=None)
    created_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))
    # Free-form rules/policies text set by group admins
    policies: Optional[str] = Field(default=None, sa_column=SAColumn(SAString, nullable=True))

    group_members: List["GroupMember"] = Relationship(back_populates="group")
    group_wallet: Optional["GroupWallet"] = Relationship(back_populates="group")
    transactions: List["Transaction"] = Relationship(back_populates="group")
    messages: List["Message"] = Relationship(back_populates="group")


class GroupMember(SQLModel, table=True):
    __tablename__ = "group_members"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    group_uid:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="groups.uid",default=None)
    user_uid:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.uid",default=None)
    is_admin: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))

    group: Optional[Group] = Relationship(back_populates="group_members")
    user: Optional[User] = Relationship(back_populates="group_members")


class GroupWallet(SQLModel, table=True):
    __tablename__ = "group_wallets"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    group_uid:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="groups.uid",default=None)
    balance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))
    updated_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))

    group: Optional[Group] = Relationship(back_populates="group_wallet")


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    transaction_type: TransactionType = Field(sa_column=SAColumn(SAEnum(TransactionType)))
    amount: float
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, sa_column=SAColumn(SAEnum(TransactionStatus)))
    description: Optional[str] = None

    from_user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid", index=True)
    to_user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid", index=True)
    group_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="groups.uid", index=True)

    phone_number: Optional[str] = None
    mobile_money_provider: Optional[str] = None
    external_reference: Optional[str] = Field(default=None, sa_column=SAColumn(SAString, unique=True, index=True))

    created_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))  
    updated_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))
    completed_at: Optional[datetime] = Field(default=None, sa_column=SAColumn(pg.TIMESTAMP(timezone=True), nullable=True))

    group: Optional[Group] = Relationship(back_populates="transactions")


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    group_uid:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="groups.uid",default=None)
    sender_uid: uuid.UUID = Field(foreign_key="users.uid", index=True)
    content: str
    created_at: datetime = Field(default_factory=now_utc, sa_column=SAColumn(pg.TIMESTAMP(timezone=True)))

    group: Optional[Group] = Relationship(back_populates="messages")
    sender: Optional[User] = Relationship(back_populates="messages") 

class HubtelEvent(SQLModel, table=True):
    __tablename__ = "hubtel_events"

    uid: uuid.UUID = Field(
        sa_column=SAColumn(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )

    # Hubtel identifiers
    external_id: Optional[str] = Field(default=None, index=True)
    transaction_id: Optional[str] = Field(default=None, index=True)
    status: Optional[str] = Field(default=None, index=True)

    # Security & processing flags
    signature_valid: bool = Field(default=False, nullable=False)
    processed: bool = Field(default=False, nullable=False)
    processing_error: Optional[str] = Field(default=None)

    # Raw payload from Hubtel
    payload: Dict[str, Any] = Field(
        sa_column=Column(JSON, nullable=False)
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": func.now()},
    )


# Helpful composite index
Index(
    "ix_hubtel_events_external_status",
    HubtelEvent.external_id,
    HubtelEvent.status,
)