import uuid
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dotenv import load_dotenv
from src.db.main import get_db
from src.db.models import User
from src.auth.auth import  verify_token
from fastapi import Request

load_dotenv()



class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials

        token_data = verify_token(token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please override this method in a child class")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data.get("refresh"):
            raise HTTPException(status_code=401, detail="Access token required")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data.get("refresh"):
            raise HTTPException(status_code=401, detail="Refresh token required")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}  # group_id -> list of websockets
    
    async def connect(self, websocket: WebSocket, group_uid: uuid.UUID):
        await websocket.accept()
        if group_uid not in self.active_connections:
            self.active_connections[group_uid] = []
        self.active_connections[group_uid].append(websocket)
    
    def disconnect(self, websocket: WebSocket, group_uid: uuid.UUID):
        if group_uid in self.active_connections:
            self.active_connections[group_uid].remove(websocket)

    async def broadcast(self, message: str, group_uid: uuid.UUID):
        if group_uid in self.active_connections:
            for connection in self.active_connections[group_uid]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# Dependency to get current user
async def get_current_user(token_data: dict = Depends(AccessTokenBearer()), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # AccessTokenBearer already verifies and returns token data
    payload = token_data
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = user_id_str
    except (ValueError, TypeError):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.uid == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user



