# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from queue import Empty, Queue

from ddeutil.core import str2bool
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import UJSONResponse
from pydantic import BaseModel

from .repeat import repeat_every

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format=(
        "%(asctime)s.%(msecs)03d (%(name)-10s, %(process)-5d, %(thread)-5d) "
        "[%(levelname)-7s] %(message)-120s (%(filename)s:%(lineno)s)"
    ),
    handlers=[logging.StreamHandler()],
    datefmt="%Y-%m-%d %H:%M:%S",
)


app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.queue = Queue()
app.output_dict = {}
app.queue_limit = 2


@app.on_event("startup")
@repeat_every(seconds=10, logger=logger)
def broker_upper_messages():
    """Broker for receive message from the `/upper` path and change it to upper
    case.
    """
    for _ in range(app.queue_limit):
        try:
            obj = app.queue.get_nowait()
            app.output_dict[obj["request_id"]] = obj["text"].upper()
            logger.info(f"Upper message: {app.output_dict}")
        except Empty:
            pass


class Payload(BaseModel):
    text: str


async def get_result(request_id):
    """Get data from output dict that global."""
    while True:
        if request_id in app.output_dict:
            result = app.output_dict[request_id]
            del app.output_dict[request_id]
            return {"message": result}
        await asyncio.sleep(0.001)


@app.post("/upper", response_class=UJSONResponse)
async def message_upper(payload: Payload):
    request_id: str = str(uuid.uuid4())
    app.queue.put(
        {"text": payload.text, "request_id": request_id},
    )
    return await get_result(request_id)


if str2bool(os.getenv("WORKFLOW_API_ENABLE_ROUTE_WORKFLOW", "true")):
    from .route import workflow

    app.include_router(workflow)

if str2bool(os.getenv("WORKFLOW_API_ENABLE_ROUTE_SCHEDULE", "true")):
    from .route import schedule

    app.include_router(schedule)
