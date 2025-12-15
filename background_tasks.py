import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from crud import task_crud
from config import settings
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundTask:
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def fetch_external_tasks(self) -> List[Dict]:
        """Получение задач с внешнего API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.EXTERNAL_API_URL, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching external tasks: {e}")
            return []
    
    async def process_external_tasks(self):
        """Обработка и сохранение задач в БД"""
        async with AsyncSessionLocal() as db:
            try:
                # Получаем задачи с внешнего API
                external_tasks = await self.fetch_external_tasks()
                
                if not external_tasks:
                    logger.info("No tasks fetched from external API")
                    return 0
                
                # Сохраняем задачи в БД
                created_tasks = await task_crud.create_tasks_batch(db, external_tasks)
                logger.info(f"Created {len(created_tasks)} tasks from external API")
                return len(created_tasks)
                
            except Exception as e:
                logger.error(f"Error processing external tasks: {e}")
                await db.rollback()
                return 0
    
    async def run_periodically(self):
        """Периодический запуск фоновой задачи"""
        self.is_running = True
        
        while self.is_running:
            try:
                logger.info("Starting background task...")
                created_count = await self.process_external_tasks()
                logger.info(f"Background task completed. Created {created_count} tasks.")
            except Exception as e:
                logger.error(f"Error in background task: {e}")
            
            # Ожидание перед следующим запуском
            await asyncio.sleep(settings.BACKGROUND_TASK_INTERVAL)
    
    def start(self):
        """Запуск фоновой задачи"""
        if not self.is_running:
            self.task = asyncio.create_task(self.run_periodically())
    
    def stop(self):
        """Остановка фоновой задачи"""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
    
    async def run_once(self) -> int:
        """Однократный запуск задачи"""
        logger.info("Manually triggering background task...")
        created_count = await self.process_external_tasks()
        logger.info(f"Manual task completed. Created {created_count} tasks.")
        return created_count

# Глобальный экземпляр фоновой задачи
background_task = BackgroundTask()