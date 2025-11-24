from graphql_query import Argument, Field, Operation, Query, Variable
import logging


log = logging.getLogger(__name__)


def generate_device_query_payload(
    device_type: str,
    site: str,
    platform: str,
    cluster: str,
    tenant: str,
    role: str,
):
    queries = [
        Query(
            name="device_type_list",
            alias="deviceType",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="deviceTypeFilter", type="DeviceTypeFilter!"),
                )
            ],
            fields=["id", "model"],
        ),
        Query(
            name="site_list",
            alias="site",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="siteFilter", type="SiteFilter!"),
                )
            ],
            fields=["id", "name", Field(name="locations", fields=["id", "name"])],
        ),
        Query(
            name="platform_list",
            alias="platform",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="platformFilter", type="PlatformFilter!"),
                )
            ],
            fields=["id", "name"],
        ),
        Query(
            name="cluster_list",
            alias="cluster",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="clusterFilter", type="ClusterFilter!"),
                )
            ],
            fields=["id", "name"],
        ),
        Query(
            name="tenant_list",
            alias="tenant",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="tenantFilter", type="TenantFilter!"),
                )
            ],
            fields=["id", "name"],
        ),
        Query(
            name="device_role_list",
            alias="role",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="deviceRoleFilter", type="DeviceRoleFilter!"),
                )
            ],
            fields=["id", "name"],
        ),
    ]

    operation = Operation(
        type="query",
        name="GetDeviceCreationIDs",
        queries=queries,
        variables=[
            Variable(name="deviceTypeFilter", type="DeviceTypeFilter!"),
            Variable(name="siteFilter", type="SiteFilter!"),
            Variable(name="platformFilter", type="PlatformFilter!"),
            Variable(name="clusterFilter", type="ClusterFilter!"),
            Variable(name="tenantFilter", type="TenantFilter!"),
            Variable(name="deviceRoleFilter", type="DeviceRoleFilter!"),
        ],
    )

    variables = {
        "deviceTypeFilter": {"model": {"i_contains": device_type}},
        "siteFilter": {"name": {"i_contains": site}},
        "platformFilter": {"name": {"i_contains": platform}},
        "clusterFilter": {"name": {"i_contains": cluster}},
        "tenantFilter": {"name": {"i_contains": tenant}},
        "deviceRoleFilter": {"name": {"i_contains": role}},
    }

    return operation.render(), variables


def generate_vm_query_payload(
    device: str,
    asset_tag: str,
    platform: str,
    cluster: str,
):
    queries = [
        Query(
            name="device_list",
            alias="device",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="deviceFilter", type="DeviceFilter!"),
                )
            ],
            fields=[
                "id",
                "name",
                Field(name="site", fields=["id", "name"]),
                Field(name="location", fields=["id", "name"]),
            ],
        ),
        Query(
            name="platform_list",
            alias="platform",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="platformFilter", type="PlatformFilter!"),
                )
            ],
            fields=["id", "name"],
        ),
        Query(
            name="cluster_list",
            alias="cluster",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="clusterFilter", type="ClusterFilter!"),
                )
            ],
            fields=["id", "name"],
        ),
    ]

    operation = Operation(
        type="query",
        name="GetVMCreationIDs",
        queries=queries,
        variables=[
            Variable(name="deviceFilter", type="DeviceFilter!"),
            Variable(name="platformFilter", type="PlatformFilter!"),
            Variable(name="clusterFilter", type="ClusterFilter!"),
        ],
    )

    variables = {
        "deviceFilter": {
            "OR": {
                "name": {"i_contains": device},
                "asset_tag": {"i_contains": asset_tag},
            }
        },
        "platformFilter": {"name": {"i_contains": platform}},
        "clusterFilter": {"name": {"i_contains": cluster}},
    }

    return operation.render(), variables


def generate_vdisk_query_payload(
    virtual_machine: str,
    uuid: str,
):
    queries = [
        Query(
            name="virtual_machine_list",
            alias="virtual_machine",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(
                        name="virtualMachineFilter", type="VirtualMachineFilter!"
                    ),
                )
            ],
            fields=["id", "name", Field(name="virtualdisks", fields=["id", "name"])],
        )
    ]

    operation = Operation(
        type="query",
        name="GetVirtualDiskCreationIDs",
        queries=queries,
        variables=[
            Variable(name="virtualMachineFilter", type="VirtualMachineFilter!"),
        ],
    )

    variables = {
        "virtualMachineFilter": {
            "OR": {
                "name": {"i_contains": virtual_machine},
                "serial": {"i_contains": uuid},
            }
        }
    }

    return operation.render(), variables
