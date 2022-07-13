
import logging
from typing import List

from app.vmware import client as vmware_client
from app.services import VMService
from app.db import models
from app import settings
from app import objects

LOG = logging.getLogger(__name__)


class SyncPass(Exception):
    pass


def _alg_sync(db_objects, db_obj_key_fn, os_objects, os_obj_key_fn,
              create_db_fn, update_db_fn, remove_db_fn,
              remove_allowed=True):
    """Generic sync Resources method."""
    # Objects to Dicts
    exist_objects = {db_obj_key_fn(db_obj): db_obj for db_obj in db_objects}
    new_objects = {os_obj_key_fn(os_obj): os_obj for os_obj in os_objects}

    LOG.info("Want %s, Got %s" % (len(exist_objects), len(new_objects)))

    for existed in exist_objects.values():
        if db_obj_key_fn(existed) in set(exist_objects) - set(new_objects):
            # Remove previously unknown resource.
            if not remove_allowed:
                LOG.warning("Will not remove unknown resource: %s" % db_obj_key_fn(existed))
                continue
            try:
                existed_id = db_obj_key_fn(existed)
                remove_db_fn(existed)
                LOG.info("Removed previously unknown resource: %s" % existed_id)
            except Exception as ex:
                LOG.exception(ex)
        else:
            # Update tracked resources.
            new_value = new_objects[db_obj_key_fn(existed)]
            try:
                if new_value == existed:
                    LOG.info("No change, pass update resource: %s" % db_obj_key_fn(existed))
                else:
                    LOG.info("Updated tracked resource: %s" % db_obj_key_fn(existed))
                    update_db_fn(existed, new_value)
            except SyncPass as ex:
                LOG.warning("Pass update resource: %s for: %s" % (db_obj_key_fn(existed), ex))
            except Exception as ex:
                LOG.exception(ex)

    # Track newly discovered resources.
    for os_obj in [os_obj for os_obj in new_objects.values() if
                   os_obj_key_fn(os_obj) in set(new_objects) - set(exist_objects)]:
        try:
            create_db_fn(os_obj)
            LOG.info("Tracked newly discovered resource: %s" % os_obj_key_fn(os_obj))
        except SyncPass as ex:
            LOG.warning("Pass create resource: %s for: %s" % (os_obj_key_fn(os_obj), ex))
        except Exception as ex:
            LOG.exception(ex)


def do_vms_sync(vm_service: VMService):
    def _remove_vm(db_obj: models.VM):
        LOG.info("Remove vm: %s" % db_obj.uuid)
        vm_service.delete_vm_by_uuid(db_obj.uuid)

    def _create_vm(vc_obj: objects.VM):
        LOG.info("Create vm: %s" % vc_obj.uuid)
        vm_service.create_vm(**vc_obj.to_dict())

    def _update_vm(db_obj: models.VM, vc_obj: objects.VM):
        LOG.info("Update vm from %s,\n to %s" % (db_obj, vc_obj))
        vm_service.update_vm(db_obj.uuid, values=vc_obj.to_dict())

    def _sync_vms_by_project(project_id: str, vc_vms: List[objects.VM]):
        db_vms = vm_service.get_vms(project_id=project_id)
        _alg_sync(db_objects=db_vms,
                  db_obj_key_fn=lambda obj: obj.uuid,
                  os_objects=vc_vms,
                  os_obj_key_fn=lambda obj: obj.uuid,
                  create_db_fn=_create_vm,
                  update_db_fn=_update_vm,
                  remove_db_fn=_remove_vm)

    LOG.info("Sync VMs starting...")

    for pv in vmware_client.retrieve_vc_vms(settings.VC):
        LOG.info("Start to syncing vms for project: %s" % pv.project_id)
        _sync_vms_by_project(pv.project_id, pv.vms)

    LOG.info("Sync VMs finished...")
