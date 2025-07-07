import os
import json
import datetime as dt

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from app.utils.db import db_insert
from app.constants.constants import DIR_LOGS


scheduler = AsyncIOScheduler(timezone=dt.timezone.utc)


@scheduler.scheduled_job("interval", minutes=1)
async def send_logs():
    for table in os.listdir(DIR_LOGS):
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
        files = []
        for file in os.listdir(os.path.join(DIR_LOGS, table)):
            if file.startswith(timestamp):
                continue
            filepath = os.path.join(DIR_LOGS, table, file)
            files.append(filepath)
            logs = []
            with open(filepath, "r") as file:
                for log in file.readlines():
                    if not log.strip():
                        continue
                    log_data = json.loads(log)
                    logs.append(log_data)

            db_insert(table, logs, [])
            os.remove(filepath)


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()
