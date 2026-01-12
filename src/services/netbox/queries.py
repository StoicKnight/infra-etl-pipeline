from graphql_query import Argument, Field, Operation, Query, Variable
import logging


log = logging.getLogger(__name__)


def generate_device_query_payload(
    device_name: str | None = None,
    uuid: str | None = None,
    role: str | None = None,
    tenant: str | None = None,
    platform: str | None = None,
    device_model: str | None = None,
    site: str | None = None,
    rack: str | None = None,
    ip_address: str | None = None,
    oob_ip_address: str | None = None,
    cluster_name: str | None = None,
    tags: str | None = None,
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
                "status",
                Field(name="role", fields=["id", "name"]),
                Field(name="tenant", fields=["id", "name"]),
                Field(name="platform", fields=["id", "name"]),
                Field(
                    name="device_type",
                    fields=[
                        "id",
                        "model",
                        "u_height",
                        Field(name="manufacturer", fields=["id", "name"]),
                    ],
                ),
                Field(name="site", fields=["id", "name"]),
                Field(name="location", fields=["id", "name"]),
                Field(name="rack", fields=["id", "na"]),
                "position",
                "asset_tag",
                Field(name="primary_ip4", fields=["id", "address", "dns_name"]),
                Field(name="oob_ip", fields=["id", "address"]),
                Field(name="cluster", fields=["id", "name"]),
                "serial",
                Field(
                    name="virtual_machines",
                    fields=[
                        "id",
                        "name",
                        "status",
                        "serial",
                        Field(name="platform", fields=["id", "name"]),
                        Field(
                            name="interfaces",
                            fields=[
                                "id",
                                "name",
                                Field(
                                    name="ip_addresses",
                                    fields=[
                                        "id",
                                        "address",
                                        "dns_name",
                                        Field(name="vrf", fields=["id", "name"]),
                                    ],
                                ),
                            ],
                        ),
                        Field(name="role", fields=["id", "name"]),
                        Field(name="tenant", fields=["id", "name"]),
                        "vcpus",
                        "memory",
                        Field(
                            name="virtualdisks",
                            fields=["id", "name", "size", "description"],
                        ),
                    ],
                ),
                Field(name="tags", fields=["id", "name"]),
                "custom_fields",
            ],
        ),
    ]

    operation = Operation(
        type="query",
        name="GetDeviceData",
        queries=queries,
        variables=[
            Variable(name="deviceFilter", type="DeviceFilter!"),
        ],
    )

    variables = {
        "deviceFilter": {
            "OR": {
                "name": {"i_contains": device_name},
                "role": {"name": {"i_contains": role}},
                "tenant": {"name": {"i_contains": tenant}},
                "platform": {"name": {"i_contains": platform}},
                "device_type": {"model": {"i_contains": device_model}},
                "site": {"name": {"i_contains": site}},
                "rack": {"name": {"i_contains": rack}},
                "primary_ip4": {"address": {"i_contains": ip_address}},
                "oob_ip": {"address": {"i_contains": oob_ip_address}},
                "cluster": {"name": {"i_contains": cluster_name}},
                "serial": {"i_contains": uuid},
                "tags": {"name": {"i_contains": tags}},
            }
        }
    }

    return operation.render(), variables


def generate_vm_query_payload(
    vm_name: str | None = None,
    uuid: str | None = None,
    cluster_name: str | None = None,
    host_name: str | None = None,
    ip_address: str | None = None,
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
            fields=[
                "id",
                "name",
                "serial",
                "status",
                Field(name="site", fields=["id", "name"]),
                Field(
                    name="cluster",
                    fields=["id", "name", Field(name="group", fields=["id", "name"])],
                ),
                Field(name="device", fields=["id", "name"]),
                Field(name="platform", fields=["id", "name"]),
                Field(name="role", fields=["id", "name"]),
                Field(name="tenant", fields=["id", "name"]),
                Field(
                    name="interfaces",
                    fields=[
                        "id",
                        "name",
                        Field(
                            name="ip_addresses",
                            fields=["id", "address", "dns_name", "status"],
                        ),
                        Field(name="vrf", fields=["id", "name"]),
                    ],
                ),
                "vcpus",
                "memory",
                Field(
                    name="virtualdisks", fields=["id", "name", "size", "description"]
                ),
                Field(name="tags", fields=["id", "name"]),
                "custom_fields",
            ],
        )
    ]

    operation = Operation(
        type="query",
        name="GetVirtualMachineData",
        queries=queries,
        variables=[
            Variable(name="virtualMachineFilter", type="VirtualMachineFilter!"),
        ],
    )

    variables = {
        "virtualMachineFilter": {
            "OR": {
                "name": {"i_contains": vm_name},
                "serial": {"i_contains": uuid},
                "cluster": {"name": {"i_contains": cluster_name}},
                "device": {"name": {"i_contains": host_name}},
                "interfaces": {"ip_addresses": {"address": {"i_contains": ip_address}}},
            }
        }
    }

    return operation.render(), variables
