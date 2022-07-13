"""Application module."""

import logging

from fastapi import FastAPI

from .container import Container
from . import endpoints

LOG = logging.getLogger(__name__)


def create_app() -> FastAPI:
    container = Container()

    db = container.db()
    db.create_database()

    api = FastAPI()
    api.container = container
    api.include_router(endpoints.router)
    return api


app = create_app()

