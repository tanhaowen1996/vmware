"""Containers module."""

from dependency_injector import containers, providers

from app.db.database import Database
from app.db.repositories import VMRepository
from app.services import VMService
from app.settings import MYSQL_URL


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])
    db = providers.Singleton(Database, db_url=MYSQL_URL)
    vm_repository = providers.Factory(
        VMRepository,
        session_factory=db.provided.session,
    )
    vm_service = providers.Factory(
        VMService,
        vm_repository=vm_repository,
    )


