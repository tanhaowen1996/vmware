"""Repositories module."""

import logging

from contextlib import AbstractContextManager
from typing import Callable, Iterator, Optional, List

from sqlalchemy.orm import Session

from .models import VM

LOG = logging.getLogger(__name__)


def query_model(session,
                project_id: Optional[str] = None,
                uuid: Optional[str] = None,
                name: Optional[str] = None,
                host: Optional[str] = None,
                ip: Optional[str] = None):
    query = session.query(VM)
    if project_id:
        query = query.filter(VM.project_id == project_id)
    if uuid:
        query = query.filter(VM.uuid == uuid)
    if name:
        query = query.filter(VM.name == name)
    if host:
        query = query.filter(VM.host == host)
    if ip:
        query = query.filter(VM.ip == ip)
    return query


def is_paged(page: int = 0, page_size: int = 0):
    if page > 0 and page_size > 0:
        return True
    return False


class VMRepository:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_all(self, page: int = 0, page_size: int = 0,
                project_id: Optional[str] = None,
                uuid: Optional[str] = None, name: Optional[str] = None,
                host: Optional[str] = None, ip: Optional[str] = None) -> Iterator[VM]:
        with self.session_factory() as session:
            query = query_model(session, project_id, uuid, name, host, ip)
            if is_paged(page, page_size):
                skip = (page - 1) * page_size
                limit = page_size
                query = query.offset(skip).limit(limit)
            return query.all()

    def get_count(self, project_id: Optional[str] = None,
                  uuid: Optional[str] = None, name: Optional[str] = None,
                  host: Optional[str] = None, ip: Optional[str] = None) -> int:
        with self.session_factory() as session:
            query = query_model(session, project_id, uuid, name, host, ip)
            return query.count()

    def get_by_uuid(self, uuid: str) -> VM:
        with self.session_factory() as session:
            vm = session.query(VM).filter(VM.uuid == uuid).first()
            if not vm:
                raise VMNotFoundError(uuid)
            return vm

    def get_by_uuids(self, uuids: List[str]) -> List[VM]:
        with self.session_factory() as session:
            return session.query(VM).filter(VM.uuid.in_(uuids)).all()

    def create(self, **kwargs) -> VM:
        with self.session_factory() as session:
            db_obj = VM()
            for k, v in kwargs.items():
                LOG.info("set %s : %s" % (k, v))
                setattr(db_obj, k, v)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj

    def delete_by_uuid(self, uuid: str) -> None:
        with self.session_factory() as session:
            entity: VM = session.query(VM).filter(VM.uuid == uuid).first()
            if not entity:
                raise VMNotFoundError(uuid)
            session.delete(entity)
            session.commit()

    def update(self, uuid: str, **values) -> VM:
        with self.session_factory() as session:
            session.query(VM).filter(VM.uuid == uuid).update(**values)
            session.commit()
        return self.get_by_uuid(uuid)


class NotFoundError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class VMNotFoundError(NotFoundError):
    entity_name: str = "VM"

