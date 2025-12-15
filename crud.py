from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models import Task
from schemas import TaskCreate, TaskUpdate
from typing import List, Optional

class TaskCRUD:
    
    @staticmethod
    async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Task]:
        query = select(Task).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
        query = select(Task).where(Task.id == task_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_task(db: AsyncSession, task: TaskCreate) -> Task:
        db_task = Task(**task.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        # Получаем задачу
        task = await TaskCRUD.get_task(db, task_id)
        if not task:
            return None
        
        # Обновляем только переданные поля
        update_data = task_update.model_dump(exclude_unset=True)
        if not update_data:
            return task
        
        query = (
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
            .returning(Task)
        )
        
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> bool:
        task = await TaskCRUD.get_task(db, task_id)
        if not task:
            return False
        
        query = delete(Task).where(Task.id == task_id)
        await db.execute(query)
        await db.commit()
        return True
    
    @staticmethod
    async def create_tasks_batch(db: AsyncSession, tasks_data: List[dict]) -> List[Task]:
        tasks = []
        for task_data in tasks_data:
            # Преобразуем данные от внешнего API
            task = Task(
                title=task_data.get('title', ''),
                description=f"From external API: User {task_data.get('userId', 'unknown')}",
                completed=task_data.get('completed', False)
            )
            db.add(task)
            tasks.append(task)
        
        await db.commit()
        
        # Refresh всех задач
        for task in tasks:
            await db.refresh(task)
        
        return tasks

task_crud = TaskCRUD()