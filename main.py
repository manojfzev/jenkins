import re
import sys

import typing

import google.cloud.compute_v1 as compute_v1


def create_instance(
    project_id: str,
    zone: str,
    instance_name: str,
    machine_type: str = "n1-standard-1",
    source_image: str = "projects/debian-cloud/global/images/family/debian-10",
    network_name: str = "global/networks/default",
) -> compute_v1.Instance:
   
    instance_client = compute_v1.InstancesClient()
    operation_client = compute_v1.ZoneOperationsClient()

    # Describe the size and source image of the boot disk to attach to the instance.
    disk = compute_v1.AttachedDisk()
    initialize_params = compute_v1.AttachedDiskInitializeParams()
    initialize_params.source_image = (
        source_image  # "projects/debian-cloud/global/images/family/debian-10"
    )
    initialize_params.disk_size_gb = 10
    disk.initialize_params = initialize_params
    disk.auto_delete = True
    disk.boot = True
    disk.type_ = "PERSISTENT"

    # Use the network interface provided in the network_name argument.
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = network_name

    # Collect information into the Instance object.
    instance = compute_v1.Instance()
    instance.name = instance_name
    instance.disks = [disk]
    if re.match(r"^zones/[a-z\d\-]+/machineTypes/[a-z\d\-]+$", machine_type):
        instance.machine_type = machine_type
    else:
        instance.machine_type = f"zones/{zone}/machineTypes/{machine_type}"
    instance.network_interfaces = [network_interface]

    # Prepare the request to insert an instance.
    request = compute_v1.InsertInstanceRequest()
    request.zone = zone
    request.project = project_id
    request.instance_resource = instance

    # Wait for the create operation to complete.
    print(f"Creating the {instance_name} instance in {zone}...")
    operation = instance_client.insert_unary(request=request)
    while operation.status != compute_v1.Operation.Status.DONE:
        operation = operation_client.wait(
            operation=operation.name, zone=zone, project=project_id
        )
    if operation.error:
        print("Error during creation:", operation.error, file=sys.stderr)
    if operation.warnings:
        print("Warning during creation:", operation.warnings, file=sys.stderr)
    print(f"Instance {instance_name} created.")
    return instance

def main(project_id: str, zone: str, instance_name: str) -> None:

    create_instance(project_id, zone, instance_name)


if __name__ == "__main__":
    import uuid
    import google.auth
    import google.auth.exceptions

    try:
        default_project_id = "gifted-loader-336417"
    except google.auth.exceptions.DefaultCredentialsError:
        print(
            "Please use `gcloud auth application-default login` "
            "or set GOOGLE_APPLICATION_CREDENTIALS to use this script."
        )
    else:
        instance_name = "jenkins-cis-cat-" + uuid.uuid4().hex[:10]
        instance_zone = "us-central1-a"
        main(default_project_id, instance_zone, instance_name)