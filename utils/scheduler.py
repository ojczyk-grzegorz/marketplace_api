import os
import json
import datetime as dt

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from datamodels.log import LogRequest
from db.db import db_insert


scheduler = AsyncIOScheduler(timezone=dt.timezone.utc)


@scheduler.scheduled_job("interval", minutes=1)
async def send_logs():
    dir_logs = "logs"
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
    files = []
    for file in os.listdir(dir_logs):
        if file.startswith(timestamp):
            continue
        filepath = os.path.join(dir_logs, file)
        files.append(filepath)
        logs = []
        with open(filepath, "r") as file:
            for log in file.readlines():
                if not log.strip():
                    continue
                log_data = json.loads(log)
                logs.append(log_data)

        db_insert(
            "logs_request",
            logs,
            columns_out=LogRequest.model_fields.keys(),
        )
        os.remove(filepath)


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()
