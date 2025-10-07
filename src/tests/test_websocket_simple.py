import asyncio
import websockets
import json
import requests
import time


async def test_websocket():
    print("🔌 Подключаемся к WebSocket...")

    try:
        async with websockets.connect('ws://localhost:8000/ws/comments') as websocket:
            # Ждем приветственное сообщение
            welcome = await websocket.recv()
            print(f"✅ Подключено: {welcome}")

            # Подписываемся на комментарии
            await websocket.send(json.dumps({
                "type": "subscribe",
                "events": ["new_comment"]
            }))

            response = await websocket.recv()
            print(f"✅ Подписка оформлена: {response}")

            print("\n🎯 Теперь создайте комментарий через Swagger или другой терминал")
            print("⏳ Ожидаю уведомление 60 секунд...")

            # Ждем уведомление
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                data = json.loads(message)
                print(f"\n🎉 ПОЛУЧЕНО УВЕДОМЛЕНИЕ:")
                print(f"Тип: {data['type']}")
                print(f"Пользователь: {data['data']['username']}")
                print(f"Текст: {data['data']['text']}")
                print("✅ WebSocket РАБОТАЕТ!")

            except asyncio.TimeoutError:
                print("\n❌ Таймаут - уведомление не получено")
                print("Проверьте:")
                print("1. Сервер запущен")
                print("2. Создан ли комментарий")
                print("3. WebSocket эндпоинт в роутерах")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())