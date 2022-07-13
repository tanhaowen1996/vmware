
import atexit
import logging
from typing import Iterator, Optional

import pyVmomi
from pyVim.connect import SmartConnect, Disconnect

from .types import VC
from app import objects

LOG = logging.getLogger(__name__)


def connect(host, user, password, port, insecure=True):
    """
    Determine the most perferred API version supported by the specified server,
    then connect to the specified server using that API version, login and return the service instance object.
    """

    service_instance = None

    try:
        service_instance = SmartConnect(host=host,
                                        user=user,
                                        pwd=password,
                                        port=port,
                                        disableSslCertValidation=insecure)
        # doing this means you don't need to remember to disconnect your script/objects
        atexit.register(Disconnect, service_instance)
    except IOError as io_error:
        print(io_error)

    if not service_instance:
        raise SystemExit("Unable to connect to host with supplied credentials.")

    return service_instance


def get_obj(content, vim_type, name, folder=None, recurse=True):
    """
    Retrieves the managed object for the name and type specified
    Throws an exception if of not found.
    Sample Usage:
    get_obj(content, [vim.Datastore], "Datastore Name")
    """
    obj = search_for_obj(content, vim_type, name, folder, recurse)
    if not obj:
        raise RuntimeError("Managed Object " + name + " not found.")
    return obj


def search_for_obj(content, vim_type, name, folder=None, recurse=True):
    """
    Search the managed object for the name and type specified
    Sample Usage:
    get_obj(content, [vim.Datastore], "Datastore Name")
    """
    if folder is None:
        folder = content.rootFolder

    obj = None
    container = content.viewManager.CreateContainerView(folder, vim_type, recurse)

    for managed_object_ref in container.view:
        if managed_object_ref.name == name:
            obj = managed_object_ref
            break
    container.Destroy()
    return obj


def _split_project_id(project_dir_name):
    """
    project_dir_name: "Project (3eadf579dcb04c7d980ecb235ea439ac)"
    return: "3eadf579dcb04c7d980ecb235ea439ac"
    """
    try:
        return project_dir_name.split('(')[1].split(')')[0]
    except Exception as e:
        raise Exception("split project_dir: %s failed: %s" % (project_dir_name, e))


def _split_vm_name_uuid(vm_dir_name):
    """
    vm_dir_name: "asdfghjk (8429558a-4606-48b7-80c4-982e59b82c1d)"
    return: ("asdfghjk", "8429558a-4606-48b7-80c4-982e59b82c1d")
    """
    try:
        arr = vm_dir_name.split('(')
        return arr[0].strip(), arr[1].split(')')[0]
    except Exception as e:
        raise Exception("split vm_dir: %s failed: %s" % (vm_dir_name, e))


def extract_vm_info(project_id, vm) -> Optional[objects.VM]:
    vm_info = None

    try:
        name, uuid = _split_vm_name_uuid(vm.name)
        # tags
        tags = [t.name for t in vm.tag]
        # summary
        summary = vm.summary
        vm_info = objects.VM(uuid=uuid,
                             project_id=project_id,
                             name=name,
                             hypervisor_uuid=summary.config.uuid,
                             host=summary.runtime.host.name,
                             cluster=summary.runtime.host.parent.name,
                             power_state=summary.runtime.powerState,
                             ip=summary.guest.ipAddress,
                             guest_id=summary.guest.guestId,
                             guest_full_name=summary.guest.guestFullName,
                             hostname=summary.guest.hostName,
                             tags=tags)
    except Exception as e:
        LOG.warning(e)
        pass

    return vm_info


def retrieve_vc_vms(vc: VC) -> Iterator[objects.ProjectVMs]:
    si = connect(host=vc.host,
                 user=vc.user,
                 password=vc.password,
                 port=vc.port,
                 insecure=vc.insecure)
    content = si.RetrieveContent()
    # get dc
    dc = get_obj(content, [pyVmomi.vim.Datacenter], vc.dc, content.rootFolder)
    # get OpenStack folder
    osfolder = get_obj(content, [pyVmomi.vim.Folder], "OpenStack", dc.vmFolder)
    # retrieve os folder child entity
    for project_folder in osfolder.childEntity:
        vms = []
        project_id = _split_project_id(project_folder.name)
        vms_folder = get_obj(content, [pyVmomi.vim.Folder], "Instances", project_folder)
        for vm in vms_folder.childEntity:
            vm_info = extract_vm_info(project_id, vm)
            if not vm_info:
                continue
            vms.append(vm_info)
        yield objects.ProjectVMs(project_id=project_id, vms=vms)
