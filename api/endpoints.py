from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import asyncio

from database import get_db
from schemas import TaskCreate, TaskUpdate, TaskResponse
from crud import task_crud
from background_tasks import background_task
from websocket import manager

router = APIRouter()

# REST API для задач
@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить список задач"""
    tasks = await task_crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить задачу по ID"""
    task = await task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую задачу"""
    created_task = await task_crud.create_task(db, task)

    # Готовим сериализуемые данные через Pydantic, чтобы избежать state из ORM
    task_payload = TaskResponse.model_validate(created_task).model_dump()

    # Отправляем уведомление через WebSocket
    await manager.broadcast_json(
        "task_created",
        {"task": task_payload}
    )

    return created_task

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить задачу (частичное обновление)"""
    updated_task = await task_crud.update_task(db, task_id, task_update)
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task_payload = TaskResponse.model_validate(updated_task).model_dump()

    # Отправляем уведомление через WebSocket
    await manager.broadcast_json(
        "task_updated",
        {"task": task_payload}
    )
    
    return updated_task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить задачу"""
    success = await task_crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Отправляем уведомление через WebSocket
    await manager.broadcast_json(
        "task_deleted",
        {"task_id": task_id}
    )

@router.post("/task-generator/run")
async def run_background_task():
    """Принудительный запуск фоновой задачи"""
    try:
        created_count = await background_task.run_once()
        
        # Отправляем уведомление через WebSocket
        await manager.broadcast_json(
            "background_task_completed",
            {"created_count": created_count}
        )
        
        return {
            "message": "Background task executed successfully",
            "tasks_created": created_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running background task: {str(e)}"
        )
