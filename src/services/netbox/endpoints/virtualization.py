from typing import TYPE_CHECKING, AsyncGenerator, List, Union

from src.services.netbox.models import (
    PaginatedVirtualMachineList,
    PatchedVirtualMachineWithId,
    VirtualMachine,
    WritableVirtualMachine,
    PaginatedClusterList,
    PatchedClusterWithId,
    Cluster,
    WritableCluster,
)

if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient

WritableVirtualMachines = Union[WritableVirtualMachine, List[WritableVirtualMachine]]
PatchedVirtualMachines = Union[
    PatchedVirtualMachineWithId, List[PatchedVirtualMachineWithId]
]
VirtualMachineIDs = Union[int, List[int]]

WritableClusters = Union[WritableCluster, List[WritableCluster]]
PatchedClusters = Union[PatchedClusterWithId, List[PatchedClusterWithId]]
ClusterIDs = Union[int, List[int]]


class VirtualMachinesEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/virtualization/virtual-machines/"

    async def list(self, **params) -> AsyncGenerator[VirtualMachine, None]:
        async for virtual_machine in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedVirtualMachineList, **params
        ):
            yield virtual_machine

    async def get(self, virtual_machine_id: int) -> VirtualMachine:
        url = f"{self.__PATH}{virtual_machine_id}/"
        return await self.__client.get(url, response_model=VirtualMachine)

    async def create(
        self, virtual_machine_data: WritableVirtualMachines
    ) -> Union[VirtualMachine, List[VirtualMachine]]:
        return await self.__client.create(
            url=self.__PATH, data=virtual_machine_data, response_model=VirtualMachine
        )

    async def update(
        self, virtual_machine_data: PatchedVirtualMachines
    ) -> Union[VirtualMachine, List[VirtualMachine]]:
        if isinstance(virtual_machine_data, PatchedVirtualMachineWithId):
            url = f"{self.__PATH}{virtual_machine_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=virtual_machine_data, response_model=VirtualMachine
        )

    async def delete(self, virtual_machine_ids: VirtualMachineIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=virtual_machine_ids)


class ClustersEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/virtualization/clusters/"

    async def list(self, **params) -> AsyncGenerator[Cluster, None]:
        async for cluster in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedClusterList, **params
        ):
            yield cluster

    async def get(self, cluster_id: int) -> Cluster:
        url = f"{self.__PATH}{cluster_id}/"
        return await self.__client.get(url, response_model=Cluster)

    async def create(
        self, cluster_data: WritableClusters
    ) -> Union[Cluster, List[Cluster]]:
        return await self.__client.create(
            url=self.__PATH, data=cluster_data, response_model=Cluster
        )

    async def update(
        self, cluster_data: PatchedClusters
    ) -> Union[Cluster, List[Cluster]]:
        if isinstance(cluster_data, PatchedClusterWithId):
            url = f"{self.__PATH}{cluster_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=cluster_data, response_model=Cluster
        )

    async def delete(self, cluster_ids: ClusterIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=cluster_ids)
