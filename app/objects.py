
from typing import List
from pydantic import BaseModel
from app.db import models


def _compare_vm_attributes(obj_a, obj_b):
    vm_ignore_fields = ('id', 'created_on', 'updated_on')
    for name in obj_a.__dict__.keys():
        if name in vm_ignore_fields:
            continue
        if name == 'tags':
            tags_a = getattr(obj_a, name)
            tags_b = getattr(obj_b, name)
            if set(tags_a) != set(tags_b):
                return False
            continue
        if getattr(obj_a, name) != getattr(obj_b, name):
            return False
    return True


class VM(BaseModel):
    uuid: str
    project_id: str
    name: str
    hypervisor_uuid: str
    host: str
    cluster: str
    hostname: str = None
    ip: str = None
    power_state: str
    guest_id: str = None
    guest_full_name: str = None
    tags: list[str]

    class Config:
        orm_mode = True

    def __eq__(self, other):
        return _compare_vm_attributes(self, other)

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def create(cls, db_obj: models.VM):
        return cls(
            uuid=db_obj.uuid,
            project_id=db_obj.project_id,
            name=db_obj.name,
            hypervisor_uuid=db_obj.hypervisor_uuid,
            host=db_obj.host,
            cluster=db_obj.cluster,
            hostname=db_obj.hostname,
            ip=db_obj.ip,
            power_state=db_obj.power_state,
            guest_id=db_obj.guest_id,
            guest_full_name=db_obj.guest_full_name,
            tags=db_obj.tags,
        )

    def to_dict(self):
        return dict(
            uuid=self.uuid,
            project_id=self.project_id,
            name=self.name,
            hypervisor_uuid=self.hypervisor_uuid,
            host=self.host,
            cluster=self.cluster,
            hostname=self.hostname,
            ip=self.ip,
            power_state=self.power_state,
            guest_id=self.guest_id,
            guest_full_name=self.guest_full_name,
            tags=self.tags,
        )


class ProjectVMs(BaseModel):
    project_id: str
    vms: List[VM]


class VMListResponse(BaseModel):
    vms: List[VM]
    total: int


class VMs(BaseModel):
    uuids: List[str]
