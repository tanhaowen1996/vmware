"""Tests module."""

from unittest import mock

import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import settings
settings.MYSQL_URL = "sqlite:///./test.db"

from .db.repositories import VMRepository, VMNotFoundError
from .db.models import VM
from .application import app


@pytest.fixture
def client():
    yield TestClient(app)


def test_get_list(client):
    repository_mock = mock.Mock(spec=VMRepository)
    repository_mock.get_all.return_value = (
        VM(id=1, uuid='1', project_id='1', name='1', hypervisor_uuid='1', host='1', cluster='1', hostname='1', ip='1',
           power_state='1', guest_id='1', guest_full_name='1', tags=['1']),
        VM(id=2, uuid='2', project_id='2', name='2', hypervisor_uuid='2', host='2', cluster='2', hostname='2', ip='2',
           power_state='2', guest_id='2', guest_full_name='2', tags=['2']),
    )
    repository_mock.get_count.return_value = 2

    with app.container.vm_repository.override(repository_mock):
        response = client.get("/vms")

    assert response.status_code == 200
    data = response.json()
    assert data == dict(
        total=2,
        vms=[
          dict(uuid='1', project_id='1', name='1', hypervisor_uuid='1', host='1', cluster='1', hostname='1', ip='1',
               power_state='1', guest_id='1', guest_full_name='1', tags=['1']),
          dict(uuid='2', project_id='2', name='2', hypervisor_uuid='2', host='2', cluster='2', hostname='2', ip='2',
               power_state='2', guest_id='2', guest_full_name='2', tags=['2']),
        ]
    )


def test_get_by_id(client):
    repository_mock = mock.Mock(spec=VMRepository)
    repository_mock.get_by_uuid.return_value = \
        VM(id=1, uuid='1', project_id='1', name='1', hypervisor_uuid='1', host='1', cluster='1', hostname='1', ip='1',
           power_state='1', guest_id='1', guest_full_name='1', tags=['1'])

    with app.container.vm_repository.override(repository_mock):
        response = client.get("/vms/1")

    assert response.status_code == 200
    data = response.json()
    assert data == \
           dict(uuid='1', project_id='1', name='1', hypervisor_uuid='1', host='1', cluster='1', hostname='1', ip='1',
                power_state='1', guest_id='1', guest_full_name='1', tags=['1'])


def test_get_by_id_404(client):
    repository_mock = mock.Mock(spec=VMRepository)
    repository_mock.get_by_uuid.side_effect = VMNotFoundError(1)

    with app.container.vm_repository.override(repository_mock):
        response = client.get("/vms/1")

    assert response.status_code == 404


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "OK"}


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "OK"}


def test_bulk_query(client):
    repository_mock = mock.Mock(spec=VMRepository)
    repository_mock.get_by_uuids.return_value = (
        VM(id=1, uuid='1', project_id='1', name='1', hypervisor_uuid='1', host='1', cluster='1', hostname='1', ip='1',
           power_state='1', guest_id='1', guest_full_name='1', tags=['1']),
        VM(id=3, uuid='3', project_id='3', name='3', hypervisor_uuid='3', host='3', cluster='3', hostname='3', ip='3',
           power_state='3', guest_id='3', guest_full_name='3', tags=[]),
    )

    with app.container.vm_repository.override(repository_mock):
        response = client.post("/vms/bulk_query", json={"uuids": ["1", "3"]})

    assert response.status_code == 200
    data = response.json()
    assert data == dict(
        total=2,
        vms=[
          dict(uuid='1', project_id='1', name='1', hypervisor_uuid='1', host='1', cluster='1', hostname='1', ip='1',
               power_state='1', guest_id='1', guest_full_name='1', tags=['1']),
          dict(uuid='3', project_id='3', name='3', hypervisor_uuid='3', host='3', cluster='3', hostname='3', ip='3',
               power_state='3', guest_id='3', guest_full_name='3', tags=[]),
        ]
    )
