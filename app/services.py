"""Services module."""

from typing import Iterator, Optional, List
from copy import deepcopy

from app.db.repositories import VMRepository
from app.db.models import VM


class VMService:

    def __init__(self, vm_repository: VMRepository) -> None:
        self._repository: VMRepository = vm_repository

    def get_vms(self, page: int = 0, page_size: int = 0,
                project_id: Optional[str] = None,
                uuid: Optional[str] = None, name: Optional[str] = None,
                host: Optional[str] = None, ip: Optional[str] = None) -> Iterator[VM]:
        return self._repository.get_all(page, page_size,
                                        project_id, uuid, name, host, ip)

    def get_count(self, project_id: Optional[str] = None,
                  uuid: Optional[str] = None, name: Optional[str] = None,
                  host: Optional[str] = None, ip: Optional[str] = None) -> int:
        return self._repository.get_count(project_id, uuid, name, host, ip)

    def get_vm_by_uuid(self, uuid: str) -> VM:
        return self._repository.get_by_uuid(uuid)

    def get_vms_by_uuids(self, uuids: List[str]) -> List[VM]:
        return self._repository.get_by_uuids(uuids)

    def create_vm(self, **kwargs) -> VM:
        return self._repository.create(**kwargs)

    def update_vm(self, uuid: str, **values: dict) -> VM:
        update_dict = deepcopy(values)
        no_changes = ('id', 'uuid', 'hypervisor_uuid', 'project_id')
        for key in no_changes:
            update_dict.pop(key, None)
        return self._repository.update(uuid, **update_dict)

    def delete_vm_by_uuid(self, uuid: str) -> None:
        return self._repository.delete_by_uuid(uuid)
