# websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio
from dataclasses import dataclass, field

from src.schema.comment import CommentOut


@dataclass
class ConnectionManager:
    active_connections: Dict[str, WebSocket] = field(default_factory=dict)

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: str):
        disconnected = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)

        for client_id in disconnected:
            self.disconnect(client_id)

    async def broadcast_new_comment(self, comment: CommentOut):
        """Рассылает новый комментарий всем подключенным клиентам"""
        message = json.dumps({
            "type": "new_comment",
            "data": {
                "id": comment.id,
                "text": comment.text,
                "username": comment.user.username,
                "created_at": comment.created_at.isoformat(),
                "parent_id": comment.parent_id,
                "has_file": bool(comment.file_path)
            }
        })
        await self.broadcast(message)

    async def broadcast_comment_deleted(self, comment_id: int):
        """Уведомляет об удалении комментария"""
        message = json.dumps({
            "type": "comment_deleted",
            "data": {"comment_id": comment_id}
        })
        await self.broadcast(message)


connection_manager = ConnectionManager()