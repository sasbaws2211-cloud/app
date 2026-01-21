import uuid
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
from dotenv import load_dotenv
from src.db.main import get_db
from src.db.models import (
    User,
    Wallet,
    Group,
    GroupMember,
    GroupWallet,
    Transaction,
    Message,
    TransactionStatus,
    TransactionType,
)
from src.schema.schemas import (
    GroupCreate,
    GroupResponse,
    ContributionRequest,
    DisbursementRequest,
    MessageResponse,
)
from src.utils import generate_invite_code
from src.auth.dependencies import get_current_user

load_dotenv()


class GroupService:
    def _utc_now_naive(self) -> datetime:
        """Return current UTC time as a timezone-naive datetime.

        This is a compatibility helper for databases that have TIMESTAMP WITHOUT TIME ZONE
        columns. Prefer updating DB columns to timestamptz long-term.
        """
        return datetime.utcnow()

    async def create_group(self, group_data: GroupCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Generate unique invite code
        invite_code = generate_invite_code()

        # Create group
        group = Group(
            name=group_data.name,
            description=group_data.description,
            contribution_amount=group_data.contribution_amount,
            contribution_frequency=group_data.contribution_frequency,
            invite_code=invite_code,
            created_by=current_user.uid,
        )

        db.add(group)
        await db.flush()

        # Add creator as admin member (set joined_at as naive UTC for compatibility)
        member = GroupMember(
            group_uid=group.uid,
            user_uid=current_user.uid,
            is_admin=True,
            joined_at=self._utc_now_naive(),
        )

        db.add(member)

        # Create group wallet
        group_wallet = GroupWallet(group_uid=group.uid)
        db.add(group_wallet)

        await db.commit()
        await db.refresh(group)

        return group

    async def get_user_groups(self, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # We need the total member count per group, but we also want to
        # restrict the returned groups to those the current user belongs to.
        # If we use the same join for both counting and filtering the current
        # user's membership the count will be limited to that user only.
        # Use a correlated subquery to compute the total members for each group.
        # Correlate the subquery to the outer Group so SQLAlchemy knows how to
        # bind the Group.uid reference inside the scalar subquery.
        member_count_subq = (
            select(func.count(GroupMember.uid))
            .where(GroupMember.group_uid == Group.uid)
            .correlate(Group)
            .scalar_subquery()
        )

        result = await db.execute(
            select(Group, GroupWallet, member_count_subq.label("member_count"))
            .join(GroupMember, Group.uid == GroupMember.group_uid)
            .join(GroupWallet, Group.uid == GroupWallet.group_uid)
            .where(GroupMember.user_uid == current_user.uid)
        )

        groups_data = result.all()

        groups = []
        for group, wallet, member_count in groups_data:
            group_dict = {
                "uid": group.uid,
                "name": group.name,
                "description": group.description,
                "contribution_amount": group.contribution_amount,
                "contribution_frequency": group.contribution_frequency,
                "invite_code": group.invite_code,
                "created_by": group.created_by,
                "created_at": group.created_at,
                "member_count": int(member_count) if member_count is not None else 0,
                "wallet_balance": wallet.balance,
            }
            groups.append(GroupResponse(**group_dict))

        return groups

    async def get_group(self, group_uid: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Check if user is member
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == current_user.uid)
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this group")

        result = await db.execute(select(Group).where(Group.uid == group_uid))
        group = result.scalar_one_or_none()

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Compute member count and wallet balance for the group so the
        # frontend's detail view has consistent data (member_count, wallet_balance).
        member_count_res = await db.execute(
            select(func.count(GroupMember.uid)).where(GroupMember.group_uid == group.uid)
        )
        member_count = member_count_res.scalar_one() or 0

        wallet_res = await db.execute(select(GroupWallet).where(GroupWallet.group_uid == group.uid))
        wallet = wallet_res.scalar_one_or_none()

        # Fetch members (with names and admin flag)
        members_res = await db.execute(
            select(GroupMember, User.name).join(User, GroupMember.user_uid == User.uid).where(GroupMember.group_uid == group.uid)
        )
        members_data = members_res.all()

        members = []
        for member, name in members_data:
            members.append({
                "uid": member.uid,
                "user_uid": member.user_uid,
                "name": name,
                "is_admin": bool(member.is_admin),
            })

        group_dict = {
            "uid": group.uid,
            "name": group.name,
            "description": group.description,
            "contribution_amount": group.contribution_amount,
            "contribution_frequency": group.contribution_frequency,
            "invite_code": group.invite_code,
            "created_by": group.created_by,
            "created_at": group.created_at,
            "member_count": int(member_count),
            "wallet_balance": wallet.balance if wallet is not None else 0.0,
            "members": members,
            "policies": getattr(group, "policies", None),
        }

        return group_dict

    async def join_group(self, invite_code: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Find group
        result = await db.execute(select(Group).where(Group.invite_code == invite_code))
        group = result.scalar_one_or_none()

        if not group:
            raise HTTPException(status_code=404, detail="Invalid invite code")

        # Check if already member
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group.uid, GroupMember.user_uid == current_user.uid)
            )
        )
        existing_member = result.scalar_one_or_none()

        if existing_member:
            raise HTTPException(status_code=400, detail="Already a member")

        # Add member (set joined_at naive UTC)
        member = GroupMember(
            group_uid=group.uid,
            user_uid=current_user.uid,
            is_admin=False,
            joined_at=self._utc_now_naive(),
        )

        db.add(member)
        await db.commit()

        return {"message": "Successfully joined group", "group_id": group.uid}

    async def contribute_to_group(self, group_uid: uuid.UUID, contribution_data: ContributionRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Check membership
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == current_user.uid)
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this group")

        # Get user wallet
        result = await db.execute(select(Wallet).where(Wallet.user_uid == current_user.uid))
        user_wallet = result.scalar_one_or_none()

        if not user_wallet or user_wallet.balance < contribution_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Get group wallet
        result = await db.execute(select(GroupWallet).where(GroupWallet.group_uid == group_uid))
        group_wallet = result.scalar_one_or_none()

        # Create transaction
        transaction = Transaction(
            transaction_type=TransactionType.CONTRIBUTION,
            amount=contribution_data.amount,
            status=TransactionStatus.COMPLETED,
            from_user_uid=current_user.uid,
            group_uid=group_uid,
            description="Group contribution",
            completed_at=self._utc_now_naive(),
        )

        db.add(transaction)

        # Update balances
        user_wallet.balance -= contribution_data.amount
        group_wallet.balance += contribution_data.amount
        user_wallet.updated_at = self._utc_now_naive()
        group_wallet.updated_at = self._utc_now_naive()

        await db.commit()
        await db.refresh(transaction)

        return transaction

    async def disburse_from_group(self, group_uid: uuid.UUID, disbursement_data: DisbursementRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Check if user is admin
        result = await db.execute(
            select(GroupMember).where(
                and_(
                    GroupMember.group_uid == group_uid,
                    GroupMember.user_uid == current_user.uid,
                    GroupMember.is_admin == True,
                )
            )
        )
        admin_membership = result.scalar_one_or_none()

        if not admin_membership:
            raise HTTPException(status_code=403, detail="Only admins can disburse funds")

        # Get group wallet
        result = await db.execute(select(GroupWallet).where(GroupWallet.group_uid == group_uid))
        group_wallet = result.scalar_one_or_none()

        if not group_wallet or group_wallet.balance < disbursement_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient group balance")

        # Get recipient wallet
        result = await db.execute(select(Wallet).where(Wallet.user_uid == disbursement_data.to_user_uid))
        recipient_wallet = result.scalar_one_or_none()

        if not recipient_wallet:
            raise HTTPException(status_code=404, detail="Recipient not found")

        # Create transaction
        transaction = Transaction(
            transaction_type=TransactionType.DISBURSEMENT,
            amount=disbursement_data.amount,
            status=TransactionStatus.COMPLETED,
            to_user_uid=disbursement_data.to_user_uid,
            group_uid=group_uid,
            description=disbursement_data.description,
            completed_at=self._utc_now_naive(),
        )

        db.add(transaction)

        # Update balances
        group_wallet.balance -= disbursement_data.amount
        recipient_wallet.balance += disbursement_data.amount
        group_wallet.updated_at = self._utc_now_naive()
        recipient_wallet.updated_at = self._utc_now_naive()

        await db.commit()
        await db.refresh(transaction)

        return transaction

    async def get_group_transactions(self, group_uid: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Check membership
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == current_user.uid)
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this group")

        result = await db.execute(
            select(Transaction).where(Transaction.group_uid == group_uid).order_by(Transaction.created_at.desc())
        )
        transactions = result.scalars().all()

        return transactions

    async def get_user_transactions(self, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        result = await db.execute(
            select(Transaction)
            .where((Transaction.from_user_uid == current_user.uid) | (Transaction.to_user_uid == current_user.uid))
            .order_by(Transaction.created_at.desc())
            .limit(50)
        )
        transactions = result.scalars().all()

        return transactions

    async def remove_group_member(self, group_uid: uuid.UUID, member_user_uid: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Only admins can remove members
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == current_user.uid, GroupMember.is_admin == True)
            )
        )
        admin_membership = result.scalar_one_or_none()

        if not admin_membership:
            raise HTTPException(status_code=403, detail="Only admins can remove group members")

        # Prevent removing yourself via this endpoint (admins shouldn't accidentally remove themselves)
        if str(member_user_uid) == str(current_user.uid):
            raise HTTPException(status_code=400, detail="Admins cannot remove themselves via this endpoint")

        # Find the member to remove
        result = await db.execute(
            select(GroupMember).where(and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == member_user_uid))
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        db.delete(member)
        await db.commit()

        return {"message": "Member removed"}

    async def update_group_policies(self, group_uid: uuid.UUID, policies: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Only admins can update policies
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == current_user.uid, GroupMember.is_admin == True)
            )
        )
        admin_membership = result.scalar_one_or_none()

        if not admin_membership:
            raise HTTPException(status_code=403, detail="Only admins can update group policies")

        # Load group and update policies
        result = await db.execute(select(Group).where(Group.uid == group_uid))
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        group.policies = policies
        db.add(group)
        await db.commit()
        await db.refresh(group)

        return {"message": "Policies updated", "policies": group.policies}

    # Chat/Messages endpoints
    async def get_group_messages(self, group_uid: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Check membership
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == current_user.uid)
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this group")

        result = await db.execute(
            select(Message, User.name)
            .join(User, Message.sender_uid == User.uid)
            .where(Message.group_uid == group_uid)
            .order_by(Message.created_at.asc())
            .limit(100)
        )

        messages_data = result.all()

        messages = []
        for message, sender_name in messages_data:
            msg_dict = {
                "uid": message.uid,
                "group_uid": message.group_uid,
                "sender_uid": message.sender_uid,
                "sender_name": sender_name,
                "content": message.content,
                "created_at": message.created_at,
            }
            messages.append(MessageResponse(**msg_dict))

        return messages
