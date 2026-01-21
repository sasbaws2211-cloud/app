import uuid
from fastapi import Depends,status, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dotenv import load_dotenv
import json
from src.auth.dependencies import get_current_user,AccessTokenBearer
from src.db.main import get_db, init_db
from src.db.models import User
from src.schema.schemas import (
    GroupCreate, GroupResponse, ContributionRequest, DisbursementRequest,
    TransactionResponse,MessageResponse
)
from src.service.group_service import GroupService

load_dotenv() 


group_router = APIRouter()
group_service = GroupService()
acccess_token_bearer = AccessTokenBearer()  

@group_router.post("/api/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    group = await group_service.create_group(group_data,current_user,db)
    
    return group

@group_router.get("/api/groups")
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    groups = await group_service.get_user_groups(current_user,db)
    
    return groups

@group_router.get("/api/groups/{group_uid}")
async def get_group(
    group_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    group = await group_service.get_group(group_uid,current_user,db)
    
    return group

@group_router.post("/api/groups/join/{invite_code}")
async def join_group(
    invite_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    group = await group_service.join_group(invite_code,current_user,db)
   
    # `group_service.join_group` returns a dict with the confirmation and group_id
    # (not an ORM object), so return it directly.
    return group

@group_router.post("/api/groups/{group_uid}/contribute", response_model=TransactionResponse)
async def contribute_to_group(
    group_uid: str,
    contribution_data: ContributionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transaction = await group_service.contribute_to_group(group_uid,contribution_data,current_user,db)
    
    return transaction

@group_router.post("/api/groups/{group_uid}/disburse", response_model=TransactionResponse)
async def disburse_from_group(
    group_uid: str,
    disbursement_data: DisbursementRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transaction = await group_service.disburse_from_group(group_uid, disbursement_data, current_user, db)
    return transaction


@group_router.delete("/api/groups/{group_uid}/members/{member_user_uid}")
async def remove_group_member(
    group_uid: str,
    member_user_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # delegate to service method which handles admin checks
    result = await group_service.remove_group_member(group_uid, member_user_uid, current_user, db)
    return result


@group_router.patch("/api/groups/{group_uid}/policies")
async def update_group_policies(
    group_uid: str,
    policies: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Expecting JSON body like { "policies": "text..." }
    pol_text = policies.get("policies") if isinstance(policies, dict) else None
    if pol_text is None:
        raise HTTPException(status_code=400, detail="Missing 'policies' in request body")

    result = await group_service.update_group_policies(group_uid, pol_text, current_user, db)
    return result

@group_router.get("/api/groups/{group_uid}/transactions", response_model=List[TransactionResponse])
async def get_group_transactions(
    group_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transactions = await group_service.get_group_transactions(group_uid,current_user,db)
    
    return transactions

@group_router.get("/api/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    transactions = await group_service.get_user_transactions(current_user,db)
    
    return transactions

# Chat/Messages endpoints
@group_router.get("/api/groups/{group_uid}/messages", response_model=List[MessageResponse])
async def get_group_messages(
    group_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    messages = await group_service.get_group_messages(group_uid,current_user,db)
    
    return messages