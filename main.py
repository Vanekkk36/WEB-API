from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from database import engine, Base
from api.endpoints import router as api_router
from websocket import manager
from background_tasks import background_task
from config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск при старте
    logger.info("Starting application...")
    
    # Создание таблиц в БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Запуск фоновой задачи
    background_task.start()
    logger.info("Background task started")
    
    yield
    
    # Остановка при завершении
    logger.info("Shutting down application...")
    background_task.stop()
    logger.info("Background task stopped")
    await engine.dispose()

# Создание FastAPI приложения
app = FastAPI(
    title="TODO API with WebSocket",
    description="REST API для управления задачами с WebSocket уведомлениями",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router)

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "TODO API with WebSocket and Background Tasks",
        "docs": "/docs",
        "websocket": "/ws/tasks"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy"}

# WebSocket эндпоинт
@app.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для уведомлений о задачах"""
    await manager.connect(websocket)
    
    try:
        await manager.send_personal_message(
            '{"type": "connected", "data": {"message": "Connected to TODO API WebSocket"}}',
            websocket
        )
        
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )