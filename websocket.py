from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from schemas import WSMessage

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)
    
    async def broadcast_json(self, message_type: str, data: dict):
        message = WSMessage(type=message_type, data=data)
        await self.broadcast(message.model_dump_json())

manager = ConnectionManager()
