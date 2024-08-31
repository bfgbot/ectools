import boto3
import random
import string
from typing import TypedDict

_ec2 = None


def _get_ec2():
    global _ec2
    if _ec2 is None:
        _ec2 = boto3.client("ec2")
    return _ec2


def _random_group_name():
    return "".join(random.choices(string.ascii_letters + string.digits, k=5))


def new_instances(template_name, count, group_name=None, **overrides) -> list[str]:
    """
    The function creates EC2 instances using the specified launch template and count.
    It applies tags (ectools=1 and group=<group_name>) to the instances for easy identification.
    Returns a list of the created instance IDs.

    Parameters:
    - template_name: Name of the EC2 launch template to use
    - count: Number of instances to create
    - group_name: Optional name for grouping instances (randomly generated if not provided)
    - **overrides: Additional parameters to override launch template settings

    Returns:
    - List of strings containing the IDs of the newly created instances
    """
    if group_name is None:
        group_name = _random_group_name()

    tags = [
        {"Key": "ectools", "Value": "1"},
        {"Key": "group", "Value": group_name},
    ]
    response = _get_ec2().run_instances(
        LaunchTemplate={
            "LaunchTemplateName": template_name,
            "Version": "$Latest",
        },
        MinCount=count,
        MaxCount=count,
        TagSpecifications=[{"ResourceType": "instance", "Tags": tags}],
        **overrides,
    )

    return [instance["InstanceId"] for instance in response["Instances"]]


def _get_group_name(tags):
    for tag in tags:
        if tag["Key"] == "group":
            return tag["Value"]


class InstanceStatus(TypedDict):
    instance_id: str
    group_name: str
    ip: str
    ready: bool


def get_latest_status() -> list[InstanceStatus]:
    """
    This function retrieves the latest status of EC2 instances tagged with 'ectools=1'.

    Returns:
    - A list of InstanceStatus objects, each representing the current state of an EC2 instance.
    """
    filters = [{"Name": f"tag:ectools", "Values": ["1"]}]
    response = _get_ec2().describe_instances(Filters=filters)
    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            ip = instance.get("PublicIpAddress")
            ready = instance["State"]["Name"] == "running"
            tags = instance["Tags"]
            group_name = _get_group_name(tags)
            instances.append({
                "instance_id": instance_id,
                "group_name": group_name,
                "ip": ip,
                "ready": ready,
            })
    return instances


def terminate_instances(instances: list[str]) -> None:
    """
    Terminate EC2 instances.

    Args:
        instances: List of instance IDs to terminate.
    """
    _get_ec2().terminate_instances(InstanceIds=instances)
