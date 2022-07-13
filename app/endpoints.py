
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from app.container import Container
from app.services import VMService
from app.db.repositories import VMNotFoundError
from app.objects import VM, VMListResponse, VMs


router = APIRouter()

LOG = logging.getLogger(__name__)


@router.get("/")
def root():
    return {"status": "OK"}


@router.get("/healthz")
def get_healthz():
    return {"status": "OK"}


@router.get("/vms", tags=["VMs"], response_model=VMListResponse)
@inject
def list_vms(page: int = 0, page_size: int = 0,
             project_id: Optional[str] = None,  uuid: Optional[str] = None, name: Optional[str] = None,
             host: Optional[str] = None, ip: Optional[str] = None,
             vm_service: VMService = Depends(Provide[Container.vm_service])):
    LOG.info("(%s, %s, %s, %s, %s, %s, %s)" % (page, page_size, project_id, uuid, name, host, ip))
    vms = vm_service.get_vms(page, page_size,
                             project_id, uuid, name, host, ip)
    total = vm_service.get_count(project_id, uuid, name, host, ip)
    return VMListResponse(vms=[VM.create(vm) for vm in vms], total=total)


@router.get("/vms/{uuid}", tags=["VMs"], response_model=VM)
@inject
def get_vm_by_uuid(uuid: str,
                   vm_service: VMService = Depends(Provide[Container.vm_service])):
    try:
        db_obj = vm_service.get_vm_by_uuid(uuid)
        return VM.create(db_obj)
    except VMNotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/vms/bulk_query", tags=["VMs"], response_model=VMListResponse)
@inject
def get_vms_by_uuids(vms: VMs,
                     vm_service: VMService = Depends(Provide[Container.vm_service])):
    try:
        db_vms = vm_service.get_vms_by_uuids(vms.uuids)
        return VMListResponse(vms=[VM.create(vm) for vm in db_vms], total=len(db_vms))
    except VMNotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

