import pytest

from src.etl.transform import (
    extract_core_os_pattern,
    flatten_to_target,
)


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "data": {
                    "device": [
                        {
                            "id": "8",
                            "name": "HF-LAR-XEN-BI-1",
                            "status": "active",
                            "role": {"id": "1", "name": "Hypervisor"},
                            "tenant": {"id": "1", "name": "Infrastructure"},
                            "platform": {"id": "13", "name": "XCP-ng 8.2 LTS"},
                            "device_type": {
                                "id": "22",
                                "model": "POWEREDGE R740",
                                "u_height": "2.0",
                                "manufacturer": {"id": "1", "name": "Dell"},
                            },
                            "site": {"id": "4", "name": "HFM Fintech"},
                            "location": {"id": "1", "name": "HFM 7th Floor"},
                            "rack": None,
                            "position": None,
                            "asset_tag": None,
                            "primary_ip4": None,
                            "oob_ip": None,
                            "cluster": {"id": "38", "name": "HF-LAR-XEN-BI-1"},
                            "serial": "947b9ba6-57c6-4069-bf0d-d383f1325d97",
                            "virtual_machines": [
                                {
                                    "id": "715",
                                    "name": "CYLAR-BI_COORDINATOR-190",
                                    "status": "active",
                                    "serial": "c2a625c2-85ca-05dc-1246-8fa122b40d0a",
                                    "platform": {
                                        "id": "3",
                                        "name": "Windows Server 2019",
                                    },
                                    "interfaces": [
                                        {
                                            "id": "13",
                                            "name": "Private",
                                            "ip_addresses": [
                                                {
                                                    "id": "1",
                                                    "address": "10.100.0.23/24",
                                                    "dns_name": "test.example.com",
                                                    "status": "active",
                                                    "vrf": {"id": "2", "name": "test"},
                                                }
                                            ],
                                        }
                                    ],
                                    "role": None,
                                    "tenant": None,
                                    "vcpus": "32.00",
                                    "memory": 65537,
                                    "virtualdisks": [
                                        {
                                            "id": "2173",
                                            "name": "CYLAR-BI_COORDINATOR-190 0 [xvda]",
                                            "size": 1048576,
                                            "description": "1d4f1151-d071-4330-a077-cce82fd97cea",
                                        }
                                    ],
                                },
                                {
                                    "id": "717",
                                    "name": "CYLAR-BI_DEVELOPMENT-192",
                                    "status": "active",
                                    "serial": "e2d49f47-5b40-f28b-87f4-ed4590315c32",
                                    "platform": {
                                        "id": "3",
                                        "name": "Windows Server 2019",
                                    },
                                    "interfaces": [
                                        {
                                            "id": "15",
                                            "name": "Private",
                                            "ip_addresses": [],
                                        }
                                    ],
                                    "role": None,
                                    "tenant": None,
                                    "vcpus": "32.00",
                                    "memory": 65537,
                                    "virtualdisks": [
                                        {
                                            "id": "2177",
                                            "name": "CYLAR-BI_DEVELOPMENT-192 0 [xvda]",
                                            "size": 1572864,
                                            "description": "9878c2b7-939d-4f7b-a833-f151587bb9d6",
                                        },
                                        {
                                            "id": "2178",
                                            "name": "CYLAR-BI_DEVELOPMENT-192 1 [xvdb]",
                                            "size": 951296,
                                            "description": "8364d61c-a894-402d-b004-6d5d9d4341b2",
                                        },
                                    ],
                                },
                                {
                                    "id": "716",
                                    "name": "CYLAR-BI_STAGING-189",
                                    "status": "active",
                                    "serial": "a0340c46-b903-60cb-6d63-71e7bf30dfb6",
                                    "platform": {
                                        "id": "3",
                                        "name": "Windows Server 2019",
                                    },
                                    "interfaces": [
                                        {
                                            "id": "19",
                                            "name": "Private",
                                            "ip_addresses": [],
                                        }
                                    ],
                                    "role": None,
                                    "tenant": None,
                                    "vcpus": "32.00",
                                    "memory": 262145,
                                    "virtualdisks": [
                                        {
                                            "id": "2174",
                                            "name": "CYLAR-BI_STAGING-189 0 [xvda]",
                                            "size": 1572864,
                                            "description": "078b06d1-dc78-4acf-8df6-c5ef81a9215c",
                                        },
                                        {
                                            "id": "2176",
                                            "name": "CYLAR-BI_STAGING-189 1 [xvdb]",
                                            "size": 2088960,
                                            "description": "10eba803-b196-4856-adf2-9b4cc4698967",
                                        },
                                        {
                                            "id": "2175",
                                            "name": "CYLAR-BI_STAGING-189 2 [xvdc]",
                                            "size": 951296,
                                            "description": "32e460a6-9e7f-4845-b665-ba8846274769",
                                        },
                                    ],
                                },
                            ],
                            "tags": [],
                            "custom_fields": {"salt_id": None},
                        },
                    ]
                }
            },
            {
                "device": [
                    {
                        "id": "8",
                        "role": "1",
                        "tenant": "1",
                        "platform": "13",
                        "device_type": {"id": "22", "manufacturer": "1"},
                        "site": "4",
                        "location": "1",
                        "cluster": "38",
                        "virtual_machines": [
                            {
                                "id": "715",
                                "platform": "3",
                                "interfaces": [
                                    {
                                        "id": "13",
                                        "ip_addresses": [{"id": "1", "vrf": "2"}],
                                    }
                                ],
                                "virtualdisks": ["2173"],
                            },
                            {
                                "id": "717",
                                "platform": "3",
                                "interfaces": ["15"],
                                "virtualdisks": ["2177", "2178"],
                            },
                            {
                                "id": "716",
                                "platform": "3",
                                "interfaces": ["19"],
                                "virtualdisks": ["2174", "2176", "2175"],
                            },
                        ],
                    }
                ]
            },
        ),
        (
            {
                "data": {
                    "virtual_machine": [
                        {
                            "id": "887",
                            "name": "cylar-hk-test-69",
                            "serial": "18cdb25c-d5db-eef8-5a41-bddf69c65fcd",
                            "status": "active",
                            "site": {"id": "4", "name": "HFM Fintech"},
                            "cluster": {
                                "id": "1",
                                "name": "XCP-ng-039",
                                "group": {"id": "1", "name": "CY-HQ Clusters"},
                            },
                            "device": {"id": "29", "name": "xcp-ng-039"},
                            "platform": {"id": "10", "name": "Debian 12"},
                            "role": None,
                            "tenant": None,
                            "interfaces": [
                                {"id": "111", "name": "Private", "ip_addresses": []}
                            ],
                            "vcpus": "8.00",
                            "memory": 8191,
                            "virtualdisks": [
                                {
                                    "id": "2232",
                                    "name": "cylar-hk-test-69 0 [xvda]",
                                    "size": 102400,
                                    "description": "53c957f3-9ca3-46b1-bec2-32ba7564c167",
                                },
                                {
                                    "id": "2224",
                                    "name": "cylar-infra-tools-250-0 [xvda]",
                                    "size": 102400,
                                    "description": "9b0dd404-27ca-4673-979a-b52e9ae718c8",
                                },
                            ],
                            "tags": [],
                            "custom_fields": {"salt_id": None},
                        },
                    ]
                }
            },
            {
                "virtual_machine": [
                    {
                        "id": "887",
                        "site": "4",
                        "cluster": {"id": "1", "group": "1"},
                        "device": "29",
                        "platform": "10",
                        "interfaces": ["111"],
                        "virtualdisks": ["2232", "2224"],
                    }
                ]
            },
        ),
    ],
    ids=["Devices", "Virtual Machines"],
)
def test_extract_ids_from_query(data, expected):
    actual = flatten_to_target(data=data, target_key="id")
    assert actual == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "Microsoft Windows Server 2019 Standard|C:\\Windows|\\Device\\Harddisk0\\Partition4",
            "Windows Server 2019",
        ),
        ("Debian GNU/Linux 12 (bookworm)", "Debian 12"),
        ("XCP-ng 8.2.1 LTS", "XCP-ng 8.2"),
        ("CentOS Linux 8", "CentOS 8"),
        ("Ubuntu Linux Server 20.04 LTS", "Ubuntu 20.04"),
    ],
    ids=["Windows Server", "Debian", "XCP-ng", "CentOS", "Ubuntu"],
)
def test_extract_core_os_pattern(input, expected):
    actual = extract_core_os_pattern(text=input)
    assert actual == expected
