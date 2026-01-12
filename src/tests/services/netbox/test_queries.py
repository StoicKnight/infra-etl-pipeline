import pytest
from services.netbox.queries import (
    generate_device_query_payload,
    generate_vm_query_payload,
)


test_cases = {
    "generate_device_query_payload": [
        (
            {
                "device_name": "HF-LAR-XEN-BI-1",
                "uuid": "",
                "role": "",
                "tenant": "",
                "platform": "",
                "device_model": "",
                "site": "",
                "rack": None,
                "ip_address": None,
                "oob_ip_address": None,
                "cluster_name": "",
                "tags": None,
            },
            (
                "query GetDeviceData(\n  $deviceFilter: DeviceFilter!\n) {\n  device: device_list(\n    filters: $deviceFilter\n  ) {\n    id\n    name\n    status\n    role {\n      id\n      name\n    }\n    tenant {\n      id\n      name\n    }\n    platform {\n      id\n      name\n    }\n    device_type {\n      id\n      model\n      u_height\n      manufacturer {\n        id\n        name\n      }\n    }\n    site {\n      id\n      name\n    }\n    location {\n      id\n      name\n    }\n    rack {\n      id\n      na\n    }\n    position\n    asset_tag\n    primary_ip4 {\n      id\n      address\n      dns_name\n    }\n    oob_ip {\n      id\n      address\n    }\n    cluster {\n      id\n      name\n    }\n    serial\n    virtual_machines {\n      id\n      name\n      status\n      serial\n      platform {\n        id\n        name\n      }\n      interfaces {\n        id\n        name\n        ip_addresses {\n          id\n          address\n          dns_name\n          vrf {\n            id\n            name\n          }\n        }\n      }\n      role {\n        id\n        name\n      }\n      tenant {\n        id\n        name\n      }\n      vcpus\n      memory\n      virtualdisks {\n        id\n        name\n        size\n        description\n      }\n    }\n    tags {\n      id\n      name\n    }\n    custom_fields\n  }\n}",
                {
                    "deviceFilter": {
                        "OR": {
                            "name": {"i_contains": "HF-LAR-XEN-BI-1"},
                            "role": {"name": {"i_contains": ""}},
                            "tenant": {"name": {"i_contains": ""}},
                            "platform": {"name": {"i_contains": ""}},
                            "device_type": {"model": {"i_contains": ""}},
                            "site": {"name": {"i_contains": ""}},
                            "rack": {"name": {"i_contains": None}},
                            "primary_ip4": {"address": {"i_contains": None}},
                            "oob_ip": {"address": {"i_contains": None}},
                            "cluster": {"name": {"i_contains": ""}},
                            "serial": {"i_contains": ""},
                            "tags": {"name": {"i_contains": None}},
                        }
                    }
                },
            ),
        ),
    ],
    "generate_vm_query_payload": [
        (
            {
                "vm_name": "",
                "uuid": "",
                "cluster_name": "",
                "host_name": "",
                "ip_address": "10.100.0.23",
            },
            (
                "query GetVirtualMachineData(\n  $virtualMachineFilter: VirtualMachineFilter!\n) {\n  virtual_machine: virtual_machine_list(\n    filters: $virtualMachineFilter\n  ) {\n    id\n    name\n    serial\n    status\n    site {\n      id\n      name\n    }\n    cluster {\n      id\n      name\n      group {\n        id\n        name\n      }\n    }\n    device {\n      id\n      name\n    }\n    platform {\n      id\n      name\n    }\n    role {\n      id\n      name\n    }\n    interfaces {\n      id\n      name\n      class_type\n      ip_addresses {\n        id\n        address\n        dns_name\n        status\n      }\n      vrf {\n        id\n        name\n      }\n    }\n    vcpus\n    memory\n    virtualdisks {\n      id\n      name\n      size\n      description\n    }\n    custom_fields\n  }\n}",
                {
                    "virtualMachineFilter": {
                        "OR": {
                            "name": {"i_contains": ""},
                            "serial": {"i_contains": ""},
                            "cluster": {"name": {"i_contains": ""}},
                            "device": {"name": {"i_contains": ""}},
                            "interfaces": {
                                "ip_addresses": {
                                    "address": {"i_contains": "10.100.0.23"}
                                }
                            },
                        }
                    }
                },
            ),
        ),
    ],
}


@pytest.mark.parametrize("input, expected", test_cases["generate_device_query_payload"])
def test_generate_device_query_payload(input, expected):
    actual = generate_device_query_payload(
        device_name=input["device_name"],
        uuid=input["uuid"],
        role=input["role"],
        tenant=input["tenant"],
        platform=input["platform"],
        device_model=input["device_model"],
        site=input["site"],
        rack=input["rack"],
        ip_address=input["ip_address"],
        oob_ip_address=input["oob_ip_address"],
        cluster_name=input["cluster_name"],
        tags=input["tags"],
    )
    assert actual == expected


@pytest.mark.parametrize("input, expected", test_cases["generate_vm_query_payload"])
def test_generate_vm_query_payload(input, expected):
    actual = generate_vm_query_payload(
        vm_name=input["vm_name"],
        uuid=input["uuid"],
        cluster_name=input["cluster_name"],
        host_name=input["host_name"],
        ip_address=input["ip_address"],
    )
    assert actual == expected
