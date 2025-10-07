# routes/websocket.py
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import uuid

from src.core.websocket import connection_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())

    await connection_manager.connect(websocket, client_id)

    try:
        while True:
            # Клиент может отправлять ping сообщения
            data = await websocket.receive_text()

            # Обработка входящих сообщений от клиента
            if data == "ping":
                await connection_manager.send_personal_message("pong", client_id)
            elif data == "get_connections":
                active_count = len(connection_manager.active_connections)
                await connection_manager.send_personal_message(
                    f"Active connections: {active_count}", client_id
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error for {client_id}: {e}")
        connection_manager.disconnect(client_id)


# routes/websocket.py (дополняем)
@router.websocket("/ws/comments")
async def comments_websocket(websocket: WebSocket):
    """Специализированный WebSocket для комментариев"""
    client_id = str(uuid.uuid4())

    await connection_manager.connect(websocket, client_id)

    try:
        # Отправляем приветственное сообщение
        await connection_manager.send_personal_message(
            json.dumps({
                "type": "welcome",
                "data": {
                    "client_id": client_id,
                    "message": "Connected to comments feed"
                }
            }),
            client_id
        )

        while True:
            data = await websocket.receive_text()

            # Обрабатываем команды от клиента
            try:
                message = json.loads(data)

                if message.get("type") == "subscribe":
                    # Клиент подписывается на определенные события
                    await connection_manager.send_personal_message(
                        json.dumps({
                            "type": "subscribed",
                            "data": {"events": message.get("events", ["new_comment"])}
                        }),
                        client_id
                    )

                elif message.get("type") == "ping":
                    await connection_manager.send_personal_message(
                        json.dumps({"type": "pong", "data": {"timestamp": "..."}}),
                        client_id
                    )

            except json.JSONDecodeError:
                # Не JSON сообщение
                await connection_manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "data": {"message": "Invalid JSON format"}
                    }),
                    client_id
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error for {client_id}: {e}")
        connection_manager.disconnect(client_id)