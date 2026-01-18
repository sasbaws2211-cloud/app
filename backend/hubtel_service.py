from typing import Optional
import random
import time

class MockHubtelService:
    """Mock implementation of Hubtel mobile money integration for testing"""
    
    def __init__(self):
        self.api_id = "mock_api_id"
        self.api_key = "mock_api_key"
    
    async def initiate_deposit(self, phone_number: str, amount: float, provider: str) -> dict:
        """
        Mock deposit initiation - simulates receiving money from customer
        In production, this would call Hubtel's receive money API
        """
        # Simulate API processing time
        await self._simulate_delay()
        
        # Generate mock transaction ID
        transaction_id = f"MOCK_DEP_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Randomly simulate success/failure (90% success rate)
        success = random.random() < 0.9
        
        return {
            "status": "success" if success else "pending",
            "transaction_id": transaction_id,
            "message": "Deposit initiated. Customer will receive prompt on their phone." if success else "Transaction pending",
            "amount": amount,
            "phone_number": phone_number,
            "provider": provider
        }
    
    async def initiate_withdrawal(self, phone_number: str, amount: float, provider: str) -> dict:
        """
        Mock withdrawal initiation - simulates sending money to customer
        In production, this would call Hubtel's send money API
        """
        await self._simulate_delay()
        
        transaction_id = f"MOCK_WD_{int(time.time())}_{random.randint(1000, 9999)}"
        success = random.random() < 0.9
        
        return {
            "status": "success" if success else "pending",
            "transaction_id": transaction_id,
            "message": "Withdrawal initiated. Money will be sent to customer's mobile wallet." if success else "Transaction pending",
            "amount": amount,
            "phone_number": phone_number,
            "provider": provider
        }
    
    async def check_transaction_status(self, transaction_id: str) -> dict:
        """
        Mock transaction status check
        In production, this would query Hubtel's API for transaction status
        """
        await self._simulate_delay(0.5)
        
        # Simulate various statuses
        statuses = ["completed", "pending", "failed"]
        weights = [0.8, 0.15, 0.05]  # 80% completed, 15% pending, 5% failed
        
        status = random.choices(statuses, weights=weights)[0]
        
        return {
            "transaction_id": transaction_id,
            "status": status,
            "message": f"Transaction {status}"
        }
    
    async def _simulate_delay(self, seconds: float = 1.0):
        """Simulate API call delay"""
        import asyncio
        await asyncio.sleep(seconds)