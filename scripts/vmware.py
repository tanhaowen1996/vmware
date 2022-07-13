#!/usr/bin/env python3

# use: https://github.com/vmware/pyvmomi
# samples: https://github.com/vmware/pyvmomi-community-samples

import atexit
import pyVmomi
from pyVim.connect import SmartConnect, Disconnect
from dataclasses import dataclass

DEV_VC_HOST="10.209.1.254"
DEV_VC_PORT=443
DEV_VC_USERNAME="yhcmp@yhcmpvc7-dev.local"
DEV_VC_PASSWORD="m#ss9ttm2E"
DEV_VC_INSECURE=True
DEV_VC_DC="dc"

PROD_VC_HOST="10.208.1.254"
PROD_VC_PORT=443
PROD_VC_USERNAME=""
PROD_VC_PASSWORD=""
PROD_VC_INSECURE=True
PROD_VC_DC=""


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

# Shamelessly borrowed from:
# https://github.com/dnaeon/py-vconnector/blob/master/src/vconnector/core.py
def collect_properties(si, view_ref, obj_type, path_set=None,
                       include_mors=False):
    """
    Collect properties for managed objects from a view ref
    Check the vSphere API documentation for example on retrieving
    object properties:
        - http://goo.gl/erbFDz
    Args:
        si          (ServiceInstance): ServiceInstance connection
        view_ref (pyVmomi.vim.view.*): Starting point of inventory navigation
        obj_type      (pyVmomi.vim.*): Type of managed object
        path_set               (list): List of properties to retrieve
        include_mors           (bool): If True include the managed objects
                                       refs in the result
    Returns:
        A list of properties for the managed objects
    """
    collector = si.content.propertyCollector

    # Create object specification to define the starting point of
    # inventory navigation
    obj_spec = pyVmomi.vmodl.query.PropertyCollector.ObjectSpec()
    obj_spec.obj = view_ref
    obj_spec.skip = True

    # Create a traversal specification to identify the path for collection
    traversal_spec = pyVmomi.vmodl.query.PropertyCollector.TraversalSpec()
    traversal_spec.name = 'traverseEntities'
    traversal_spec.path = 'view'
    traversal_spec.skip = False
    traversal_spec.type = view_ref.__class__
    obj_spec.selectSet = [traversal_spec]

    # Identify the properties to the retrieved
    property_spec = pyVmomi.vmodl.query.PropertyCollector.PropertySpec()
    property_spec.type = obj_type

    if not path_set:
        property_spec.all = True

    property_spec.pathSet = path_set

    # Add the object and property specification to the
    # property filter specification
    filter_spec = pyVmomi.vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = [obj_spec]
    filter_spec.propSet = [property_spec]

    # Retrieve properties
    props = collector.RetrieveContents([filter_spec])

    data = []
    for obj in props:
        properties = {}
        for prop in obj.propSet:
            properties[prop.name] = prop.val

        if include_mors:
            properties['obj'] = obj.obj

        data.append(properties)
    return data


def get_container_view(si, obj_type, container=None):
    """
    Get a vSphere Container View reference to all objects of type 'obj_type'
    It is up to the caller to take care of destroying the View when no longer
    needed.
    Args:
        obj_type (list): A list of managed object types
    Returns:
        A container view ref to the discovered managed objects
    """
    if not container:
        container = si.content.rootFolder

    view_ref = si.content.viewManager.CreateContainerView(
        container=container,
        type=obj_type,
        recursive=True
    )
    return view_ref


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


def get_all_obj(content, vim_type, folder=None, recurse=True):
    """
    Search the managed object for the name and type specified
    Sample Usage:
    get_obj(content, [vim.Datastore], "Datastore Name")
    """
    if not folder:
        folder = content.rootFolder

    obj = {}
    container = content.viewManager.CreateContainerView(folder, vim_type, recurse)

    for managed_object_ref in container.view:
        obj[managed_object_ref] = managed_object_ref.name

    container.Destroy()
    return obj


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

@dataclass
class VC:
    host: str
    port: str
    user: str
    password: str
    insecure: bool
    dc: str

def main():
    use_prod = False
    vc = None

    if use_prod:
        vc = VC(PROD_VC_HOST, PROD_VC_PORT,
                PROD_VC_USERNAME, PROD_VC_PASSWORD,
                PROD_VC_INSECURE,
                PROD_VC_DC)
    else:
        vc = VC(DEV_VC_HOST, DEV_VC_PORT,
                DEV_VC_USERNAME, DEV_VC_PASSWORD,
                DEV_VC_INSECURE,
                DEV_VC_DC)

    si = connect(host=vc.host,
                 user=vc.user,
                 password=vc.password,
                 port=vc.port,
                 insecure=vc.insecure)

    vms = []

    content = si.RetrieveContent()

    # get dc
    dc = get_obj(content, [pyVmomi.vim.Datacenter], vc.dc, content.rootFolder)
    # get OpenStack folder
    osfolder = get_obj(content, [pyVmomi.vim.Folder], "OpenStack", dc.vmFolder)
    # retrieve os folder child entity
    for project_folder in osfolder.childEntity:
        project_id = _split_project_id(project_folder.name)
        vms_folder = get_obj(content, [pyVmomi.vim.Folder], "Instances", project_folder)
        for vm in vms_folder.childEntity:
            vms.append(show_vm(project_id, vm))
  
  
    """
    for child in content.rootFolder.childEntity:
        print(child.name)
        # print(dir(child))
        #print(child.vmFolder)
        #print(dir(child.vmFolder))
        print('--------------------')
        #fds = get_all_obj(content, [pyVmomi.vim.Folder], child.vmFolder)
        osvmfolder = get_obj(content, [pyVmomi.vim.Folder], "OpenStack", child.vmFolder)
        print(osvmfolder.name)
        #print(dir(osvmfolder))        

        for vf in osvmfolder.childEntity:
            #print('\t', vf)
            #print('\t', dir(vf))
            print('\t-', vf.name)
            project_id = _split_project_id(vf.name)
            ins = get_obj(content, [pyVmomi.vim.Folder], "Instances", vf)
            for i in ins.childEntity:
                #print('\t\t-', i.name)
                vms.append(show_vm(project_id, i))
    """
    print("===========================================================")

    for vm in vms:
        print(vm)

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

@dataclass
class VMInfo:
    project_id: str
    name: str
    instance_uuid: str
    guest_uuid: str
    host: str
    ip: str
    power_state: str
    guest_id: str
    guest_full_name: str
    hostname: str
    cluster: str
    tags: list[str]


def show_vm(project_id, vm):
    vm_info = None

    try:
        print(vm.name)
        vm_name, vm_uuid = _split_vm_name_uuid(vm.name)
        #print('project_id: %s, vm_name: %s, vm_uuid: %s' % (project_id, vm_name, vm_uuid))
        #print(vm.runtime.host.name)
        # print(vm.summary)
        summary = vm.summary
        # print(summary.config)
        tags = []
        for t in vm.tag:
            tags.append(t.name)
        
        vm_info = VMInfo(project_id=project_id,
                         name=vm_name,
                         instance_uuid=vm_uuid,
                         guest_uuid=summary.config.uuid,
                         host=summary.runtime.host.name,
                         cluster=summary.runtime.host.parent.name,
                         power_state=summary.runtime.powerState,
                         ip=summary.guest.ipAddress,
                         guest_id=summary.guest.guestId,
                         guest_full_name=summary.guest.guestFullName,
                         hostname=summary.guest.hostName,
                         tags=tags)
    except Exception as e:
        print(e)
        # raise e

    return vm_info


if __name__ == '__main__':
    print('Start...')
    main()
    print('Done!')

