import aiosqlite
import datetime
import asyncio
from matplotlib.pyplot import show

DATABASE = 'detections.db'

TIME_DELAY = 10

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                number_of_humans INTEGER NOT NULL
            )
        ''')
        await db.commit()

async def log_detection(number_of_humans):
    timestamp = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            INSERT INTO detections (timestamp, number_of_humans)
            VALUES (?, ?)
        ''', (timestamp, number_of_humans))
        await db.commit()

async def show_table():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT * FROM detections') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                print(row)

if __name__ == '__main__':
    asyncio.run(show_table())