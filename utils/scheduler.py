import os
import json
import datetime as dt

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from datamodels.log import LogRequest
from utils.db import db_insert


scheduler = AsyncIOScheduler(timezone=dt.timezone.utc)


@scheduler.scheduled_job("interval", minutes=1)
async def send_logs():
    dir_logs = "logs"
    for table in os.listdir(dir_logs):
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
        files = []
        for file in os.listdir(os.path.join(dir_logs, table)):
            if file.startswith(timestamp):
                continue
            filepath = os.path.join(dir_logs, table, file)
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
