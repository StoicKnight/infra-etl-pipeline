from graphql_query import Argument, Operation, Query, Variable
import logging


log = logging.getLogger(__name__)


def generate_device_creation_payload(
    device_type: str,
    site: str,
    platform: str,
    location: str,
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
            fields=["id", "name"],
        ),
        Query(
            name="location_list",
            alias="location",
            arguments=[
                Argument(
                    name="filters",
                    value=Variable(name="locationFilter", type="LocationFilter!"),
                )
            ],
            fields=["id", "name"],
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
            Variable(name="locationFilter", type="LocationFilter!"),
            Variable(name="platformFilter", type="PlatformFilter!"),
            Variable(name="clusterFilter", type="ClusterFilter!"),
            Variable(name="tenantFilter", type="TenantFilter!"),
            Variable(name="deviceRoleFilter", type="DeviceRoleFilter!"),
        ],
    )

    variables = {
        "deviceTypeFilter": {"model": {"i_contains": device_type}},
        "siteFilter": {"name": {"i_contains": site}},
        "locationFilter": {"name": {"i_contains": location}},
        "platformFilter": {"name": {"i_contains": platform}},
        "clusterFilter": {"name": {"i_contains": cluster}},
        "tenantFilter": {"name": {"i_contains": tenant}},
        "deviceRoleFilter": {"name": {"i_contains": role}},
    }

    return operation.render(), variables
