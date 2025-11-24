import pytest

from src.etl.transform import extract_ids_from_query, extract_core_os_pattern

test_cases = {
    "extract_ids_from_query": [
        (
            {
                "data": {
                    "deviceType": [
                        {"id": "22", "model": "POWEREDGE R740"},
                        {"id": "1", "model": "POWEREDGE R740xd"},
                    ],
                    "site": [
                        {"id": "5", "name": "HFGS", "locations": []},
                        {
                            "id": "4",
                            "name": "HFM Fintech",
                            "locations": [
                                {"id": "2", "name": "HFM 10th Floor"},
                                {"id": "1", "name": "HFM 7th Floor"},
                            ],
                        },
                    ],
                    "platform": [
                        {"id": "10", "name": "Debian 12"},
                        {"id": "5", "name": "Windows Server 2012 R2"},
                    ],
                    "cluster": [{"id": "19", "name": "XCP-ng-019"}],
                    "tenant": [{"id": "1", "name": "Infrastructure"}],
                    "role": [{"id": "2", "name": "MT4 Trading Server"}],
                }
            },
            {
                "deviceType": ["1", "22"],
                "site": [
                    {"id": "5", "location": []},
                    {"id": "4", "location": ["1", "2"]},
                ],
                "platform": ["10", "5"],
                "cluster": ["19"],
                "tenant": ["1"],
                "role": ["2"],
            },
        ),
        (
            {
                "data": {
                    "device": [
                        {
                            "id": "8",
                            "name": "HF-LAR-XEN-BI-1",
                            "site": {"id": "4", "name": "HFM Fintech"},
                            "location": {"id": "1", "name": "HFM 7th Floor"},
                        }
                    ],
                    "platform": [
                        {"id": "10", "name": "Debian 12"},
                    ],
                    "cluster": [
                        {"id": "38", "name": "HF-LAR-XEN-BI-1"},
                    ],
                }
            },
            {
                "device": [{"id": "8", "site": "4", "location": "1"}],
                "platform": ["10"],
                "cluster": ["38"],
            },
        ),
        (
            {
                "data": {
                    "virtual_machine": [
                        {
                            "id": "699",
                            "name": "ZA-MT4-DC-METRICS-8",
                            "virtualdisks": [
                                {"id": "5", "name": "ZA-MT4-DC-METRICS-8"}
                            ],
                        },
                        {
                            "id": "154",
                            "name": "PROMETHEUS-DEV-99",
                            "virtualdisks": [
                                {"id": "2", "name": "PROMETHEUS-DEV-99 0"},
                                {"id": "4", "name": "PROMETHEUS-DEV-99 1"},
                            ],
                        },
                    ]
                }
            },
            {
                "virtual_machine": [
                    {"id": "699", "vdisk": ["5"]},
                    {"id": "154", "vdisk": ["2", "4"]},
                ]
            },
        ),
        (  # Duplicates & Data Types
            {
                "data": {
                    "platform": [
                        {"id": "10", "name": "Debian"},
                        {"id": 10, "name": "Debian Copy"},
                        {"id": "5", "name": "Windows"},
                        {"name": "No ID Platform"},
                    ],
                    "role": [],
                }
            },
            {
                "platform": ["10", "5"],
                "role": [],
            },
        ),
        (  # Cluster Matching Logic (Many-to-Many & Case Insensitivity)
            {
                "data": {
                    "device": [
                        {"id": "1", "name": "Server-A"},
                        {"id": "2", "name": "Server-B"},
                    ],
                    "cluster": [
                        {"id": "100", "name": "server-a"},
                        {"id": "200", "name": "Server-B"},
                        {"id": "300", "name": "Server-C"},
                    ],
                }
            },
            {
                "device": [{"id": "1"}, {"id": "2"}],
                "cluster": ["100", "200"],
            },
        ),
        (  # The "Single Cluster" Exception
            {
                "data": {
                    "device": [{"id": "1", "name": "Server-X"}],
                    "cluster": [{"id": "999", "name": "Cluster-Z"}],
                }
            },
            {
                "device": [{"id": "1"}],
                "cluster": ["999"],
            },
        ),
        (  # Nested Duplicates (Site Locations)
            {
                "data": {
                    "site": [
                        {
                            "id": "5",
                            "locations": [
                                {"id": "100", "name": "Room A"},
                                {"id": 100, "name": "Room A Dup"},
                            ],
                        },
                        {"id": "6"},
                    ]
                }
            },
            {
                "site": [
                    {"id": "5", "location": ["100"]},
                    {"id": "6", "location": []},
                ],
            },
        ),
        # Empty Data / None
        ({"data": None}, {}),
    ],
    "extract_core_os_pattern": [
        (
            "Microsoft Windows Server 2019 Standard|C:\\Windows|\\Device\\Harddisk0\\Partition4",
            "Windows Server 2019",
        ),
        ("Debian GNU/Linux 12 (bookworm)", "Debian 12"),
        ("XCP-ng 8.2.1", "XCP-ng 8.2"),
        ("CentOS Linux 8", "CentOS 8"),
        ("Ubuntu Linux Server 20.04 LTS", "Ubuntu 20.04"),
    ],
}


@pytest.mark.parametrize("input, expected", test_cases["extract_ids_from_query"])
def test_extract_ids_from_query(input, expected):
    actual = extract_ids_from_query(data=input)
    assert actual == expected


@pytest.mark.parametrize("input, expected", test_cases["extract_core_os_pattern"])
def test_extract_core_os_pattern(input, expected):
    actual = extract_core_os_pattern(text=input)
    assert actual == expected
