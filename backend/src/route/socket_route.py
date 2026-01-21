import uuid
from fastapi import WebSocket, WebSocketDisconnect,APIRouter
from sqlalchemy import select, and_
from dotenv import load_dotenv
import json
from src.auth.dependencies import AccessTokenBearer
from src.db.main import get_db
from src.db.models import User,GroupMember,Message
from src.auth.auth import verify_token 
from src.auth.dependencies import manager



load_dotenv() 

socket_router = APIRouter()
acccess_token_bearer = AccessTokenBearer() 

@socket_router.websocket("/api/ws/chat/{group_uid}")
async def websocket_chat(websocket: WebSocket, group_uid: uuid.UUID, token: str):
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008)
        return
    
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008)
        return
    
    # Get database session
    async for db in get_db():
        # Check membership
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_uid == group_uid, GroupMember.user_uid == user_id)
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            await websocket.close(code=1008)
            return
        
        # Get user
        result = await db.execute(select(User).where(User.uid == user_id))
        user = result.scalar_one()
        
        await manager.connect(websocket, group_uid)
        
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Save message to database
                message = Message(
                    group_uid=group_uid,
                    sender_uid=user_id,
                    content=message_data["content"]
                )
                
                db.add(message)
                await db.commit()
                await db.refresh(message)
                
                # Broadcast to all group members (convert UUIDs to strings for JSON)
                broadcast_data = {
                    "id": str(message.uid),
                    "sender_id": str(user_id),
                    "sender_name": user.name,
                    "content": message.content,
                    "created_at": message.created_at.isoformat()
                }

                await manager.broadcast(json.dumps(broadcast_data), group_uid)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, group_uid)
        except Exception as e:
            print(f"WebSocket error: {e}")
            manager.disconnect(websocket, group_uid)

