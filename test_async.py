import asyncio
import aiohttp
import json

async def create_task(session, url, task_data):
    async with session.post(url, json=task_data) as response:
        return await response.json()

async def main():
    url = "http://localhost:8000/tasks"
    tasks_data = [
        {"title": "Задача 1", "description": "Асинхронный тест 1"},
        {"title": "Задача 2", "description": "Асинхронный тест 2"},
        {"title": "Задача 3", "description": "Асинхронный тест 3"}
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [create_task(session, url, task) for task in tasks_data]
        results = await asyncio.gather(*tasks)
        print(f"Создано задач: {len(results)}")
        for result in results:
            print(f"ID: {result['id']}, Заголовок: {result['title']}")

if __name__ == "__main__":
    asyncio.run(main())
