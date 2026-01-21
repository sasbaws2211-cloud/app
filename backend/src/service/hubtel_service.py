"""
Hubtel mobile money integration module.

- Async Hubtel client with proper Basic Auth
- Decimal-safe money handling
- Idempotent transaction support
- Mock service for local/testing
- Designed for wallet & group-wallet fintech systems

IMPORTANT:
Final transaction status MUST be resolved via Hubtel webhooks.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
import os
import asyncio
import logging
import base64
import uuid 
from src.provider import normalize_provider 
from decimal import ROUND_HALF_UP

import httpx

logger = logging.getLogger(__name__)



class HubtelService:
    """
    Async client for Hubtel Mobile Money operations.

    All initiate_* methods return PENDING.
    Final state MUST be handled via webhook.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_id: Optional[str] = None,
        api_key: Optional[str] = None,
        merchant_account: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.base_url = base_url or os.getenv("HUBTEL_BASE_URL", "https://api.hubtel.com")
        self.api_id = api_id or os.getenv("HUBTEL_API_ID")
        self.api_key = api_key or os.getenv("HUBTEL_API_KEY")
        # Merchant account number used in Hubtel merchant-account APIs (send/receive)
        self.merchant_account = merchant_account or os.getenv("HUBTEL_MERCHANT_ACCOUNT")
        self.timeout = timeout

        if not self.api_id or not self.api_key:
            raise ValueError("Hubtel API credentials are missing")

        auth = f"{self.api_id}:{self.api_key}".encode()
        self._auth_header = base64.b64encode(auth).decode()

        self._client = httpx.AsyncClient(timeout=self.timeout) 
    
    def to_hubtel_amount(amount: Decimal) -> str:
        return str(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {self._auth_header}",
        }

    async def initiate_deposit(
        self,
        phone_number: str,
        amount: Decimal,
        provider: str,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Request money from user's mobile money wallet.
        """

        # Preferred official Receive Money endpoint for Hubtel merchant accounts
        # Allow overriding via HUBTEL_RECEIVE_URL for testing/backwards-compat 
        provider_code = normalize_provider(provider)
        merchant = self.merchant_account
        if not merchant:
            raise ValueError("Hubtel merchant account number is not configured (HUBTEL_MERCHANT_ACCOUNT)")

        endpoint = os.getenv(
            "HUBTEL_RECEIVE_URL",
            f"https://rmp.hubtel.com/merchantaccount/merchants/{merchant}/receive/mobilemoney",
        )

        external_id = external_id or str(uuid.uuid4())

        payload = {
            "externalId": external_id,
            "amount": self.to_hubtel_amount(amount),
            "currency": "GHS",
            "customerPhoneNumber": phone_number,
            "provider": provider_code,
            "description": "Wallet deposit",
        }

        try:
            resp = await self._client.post(
                endpoint, json=payload, headers=self._headers()
            )
            # If Hubtel returns a non-2xx, raise to enter the HTTPStatusError handler
            resp.raise_for_status()
            data = resp.json()

            return {
                "status": "pending",
                "transaction_id": data.get("checkoutId") or external_id,
                "external_id": external_id,
                "message": "Deposit initiated",
                "raw": data,
            }

        except httpx.HTTPStatusError as e:
            # Inspect response body for debugging (Hubtel often returns JSON error details)
            resp = e.response
            body_text = None
            try:
                body_text = resp.text
            except Exception:
                body_text = '<unreadable response body>'

            logger.error("Hubtel deposit HTTP error %s %s: %s", resp.status_code, endpoint, body_text)
            return {
                "status": "failed",
                "transaction_id": None,
                "external_id": external_id,
                "message": f"HTTP {resp.status_code}: {body_text}",
                "status_code": resp.status_code,
                "raw": body_text,
            }

        except httpx.HTTPError as e:
            logger.exception("Hubtel deposit error")
            return {
                "status": "failed",
                "transaction_id": None,
                "external_id": external_id,
                "message": str(e),
            }

    async def initiate_withdrawal(
        self,
        phone_number: str,
        amount: Decimal,
        provider: str,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send money from platform wallet to user's mobile money wallet.
        """

        # Preferred official Send Money endpoint for Hubtel merchant accounts
        # Allow overriding via HUBTEL_SEND_URL for testing/backwards-compat 
        provider_code = normalize_provider(provider)

        merchant = self.merchant_account
        if not merchant:
            raise ValueError("Hubtel merchant account number is not configured (HUBTEL_MERCHANT_ACCOUNT)")

        endpoint = os.getenv(
            "HUBTEL_SEND_URL",
            f"https://smp.hubtel.com/api/merchants/{merchant}/send-mobilemoney",
        )

        external_id = external_id or str(uuid.uuid4())

        payload = {
            "externalId": external_id,
            "amount": self.to_hubtel_amount(amount),
            "currency": "GHS",
            "recipient": {
                "phoneNumber": phone_number,
                "provider": provider_code,
            },
            "description": "Wallet withdrawal",
        }

        try:
            resp = await self._client.post(
                endpoint, json=payload, headers=self._headers()
            )
            resp.raise_for_status()
            data = resp.json()

            return {
                "status": "pending",
                "transaction_id": data.get("transactionId") or external_id,
                "external_id": external_id,
                "message": "Withdrawal initiated",
                "raw": data,
            }

        except httpx.HTTPError as e:
            logger.exception("Hubtel withdrawal error")
            return {
                "status": "failed",
                "transaction_id": None,
                "external_id": external_id,
                "message": str(e),
            }

    async def close(self):
        await self._client.aclose()


class MockHubtelService:
    """
    Mock Hubtel service for local development & testing.
    """

    async def initiate_deposit(
        self,
        phone_number: str,
        amount: Decimal,
        provider: str,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return {
            "status": "pending",
            "transaction_id": f"MOCK_DEP_{uuid.uuid4().hex}",
            "external_id": external_id or str(uuid.uuid4()),
            "message": "Mock deposit initiated",
        }

    async def initiate_withdrawal(
        self,
        phone_number: str,
        amount: Decimal,
        provider: str,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return {
            "status": "pending",
            "transaction_id": f"MOCK_WD_{uuid.uuid4().hex}",
            "external_id": external_id or str(uuid.uuid4()),
            "message": "Mock withdrawal initiated",
        }


def get_hubtel_service() -> object:
    """
    Factory method to select real or mock Hubtel service.
    """

    use_mock = os.getenv("HUBTEL_USE_MOCK", "true").lower() == "true"
    api_key = os.getenv("HUBTEL_API_KEY")

    if use_mock or not api_key:
        logger.warning("Using MockHubtelService")
        return MockHubtelService()

    return HubtelService() 

def verify_hubtel_signature(
    body: bytes,
    signature: str,
    secret: str,
) -> bool:
    import hmac
    import hashlib

    digest = hmac.new(
        secret.encode(),
        body,
        hashlib.sha1,   # <-- Hubtel uses SHA1
    ).hexdigest()

    return hmac.compare_digest(digest, signature)

