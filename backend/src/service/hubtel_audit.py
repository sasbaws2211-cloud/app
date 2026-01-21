from typing import Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import HubtelEvent


async def log_hubtel_event(
    db: AsyncSession,
    *,
    payload: Dict[str, Any],
    signature_valid: bool,
    external_id: Optional[str] = None,
    transaction_id: Optional[str] = None,
    status: Optional[str] = None,
    processed: bool = False,
    error: Optional[str] = None,
) -> HubtelEvent:
    """
    Persist Hubtel webhook event (append-only).

    Never raises — audit logging must never break webhook flow.
    """
    event = HubtelEvent(
        payload=payload,
        signature_valid=signature_valid,
        external_id=external_id,
        transaction_id=transaction_id,
        status=status,
        processed=processed,
        processing_error=error,
    )

    db.add(event)
    await db.flush()   # Do NOT commit here

    return event
