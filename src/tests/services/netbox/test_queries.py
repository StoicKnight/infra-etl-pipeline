import pytest
from services.netbox.queries import (
    generate_device_query_payload,
    generate_vdisk_query_payload,
    generate_vm_query_payload,
)


test_cases = {
    "generate_device_query_payload": [
        (
            {
                "device_type": "r740",
                "site": "hfm",
                "platform": "12",
                "cluster": "1",
                "tenant": "infra",
                "role": "mt4",
            },
            (
                "query GetDeviceCreationIDs(\n  $deviceTypeFilter: DeviceTypeFilter!\n  $siteFilter: SiteFilter!\n  $platformFilter: PlatformFilter!\n  $clusterFilter: ClusterFilter!\n  $tenantFilter: TenantFilter!\n  $deviceRoleFilter: DeviceRoleFilter!\n) {\n  deviceType: device_type_list(\n    filters: $deviceTypeFilter\n  ) {\n    id\n    model\n  }\n\n  site: site_list(\n    filters: $siteFilter\n  ) {\n    id\n    name\n    locations {\n      id\n      name\n    }\n  }\n\n  platform: platform_list(\n    filters: $platformFilter\n  ) {\n    id\n    name\n  }\n\n  cluster: cluster_list(\n    filters: $clusterFilter\n  ) {\n    id\n    name\n  }\n\n  tenant: tenant_list(\n    filters: $tenantFilter\n  ) {\n    id\n    name\n  }\n\n  role: device_role_list(\n    filters: $deviceRoleFilter\n  ) {\n    id\n    name\n  }\n}",
                {
                    "deviceTypeFilter": {"model": {"i_contains": "r740"}},
                    "siteFilter": {"name": {"i_contains": "hfm"}},
                    "platformFilter": {"name": {"i_contains": "12"}},
                    "clusterFilter": {"name": {"i_contains": "1"}},
                    "tenantFilter": {"name": {"i_contains": "infra"}},
                    "deviceRoleFilter": {"name": {"i_contains": "mt4"}},
                },
            ),
        ),
    ],
    "generate_vm_query_payload": [
        (
            {
                "device": "xcp-ng-039",
                "asset_tag": "947b9",
                "platform": "12",
                "cluster": "xcp-ng-039",
            },
            (
                "query GetVMCreationIDs(\n  $deviceFilter: DeviceFilter!\n  $platformFilter: PlatformFilter!\n  $clusterFilter: ClusterFilter!\n) {\n  device: device_list(\n    filters: $deviceFilter\n  ) {\n    id\n    name\n    site {\n      id\n      name\n    }\n    location {\n      id\n      name\n    }\n  }\n\n  platform: platform_list(\n    filters: $platformFilter\n  ) {\n    id\n    name\n  }\n\n  cluster: cluster_list(\n    filters: $clusterFilter\n  ) {\n    id\n    name\n  }\n}",
                {
                    "deviceFilter": {
                        "OR": {
                            "name": {"i_contains": "xcp-ng-039"},
                            "asset_tag": {"i_contains": "947b9"},
                        }
                    },
                    "platformFilter": {"name": {"i_contains": "12"}},
                    "clusterFilter": {"name": {"i_contains": "xcp-ng-039"}},
                },
            ),
        ),
    ],
    "generate_vdisk_query_payload": [
        (
            {
                "virtual_machine": "test_vm",
                "serial": "55f287b5-026f-ec82-f840-534f0dd47429",
            },
            (
                "query GetVirtualDiskCreationIDs(\n  $virtualMachineFilter: VirtualMachineFilter!\n) {\n  virtual_machine: virtual_machine_list(\n    filters: $virtualMachineFilter\n  ) {\n    id\n    name\n    virtualdisks {\n      id\n      name\n    }\n  }\n}",
                {
                    "virtualMachineFilter": {
                        "OR": {
                            "name": {"i_contains": "test_vm"},
                            "serial": {
                                "i_contains": "55f287b5-026f-ec82-f840-534f0dd47429"
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
        device_type=input["device_type"],
        site=input["site"],
        platform=input["platform"],
        cluster=input["cluster"],
        tenant=input["tenant"],
        role=input["role"],
    )
    assert actual == expected


@pytest.mark.parametrize("input, expected", test_cases["generate_vm_query_payload"])
def test_generate_vm_query_payload(input, expected):
    actual = generate_vm_query_payload(
        device=input["device"],
        asset_tag=input["asset_tag"],
        platform=input["platform"],
        cluster=input["cluster"],
    )
    assert actual == expected


@pytest.mark.parametrize("input, expected", test_cases["generate_vdisk_query_payload"])
def test_generate_vdisk_query_payload(input, expected):
    actual = generate_vdisk_query_payload(
        virtual_machine=input["virtual_machine"], uuid=input["serial"]
    )
    assert actual == expected
