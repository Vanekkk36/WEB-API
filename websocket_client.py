import asyncio
import websockets
import json
import sys

async def websocket_client():
    uri = "ws://localhost:8000/ws/tasks"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Подключились к WebSocket!")
            print("Ждем сообщения... (Ctrl+C для выхода)")
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"\n📨 Получено сообщение:")
                    print(f"   Тип: {data['type']}")
                    print(f"   Данные: {data['data']}")
                except KeyboardInterrupt:
                    print("\n👋 Отключаемся...")
                    break
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ Не удалось подключиться: {e}")

if __name__ == "__main__":
    asyncio.run(websocket_client())