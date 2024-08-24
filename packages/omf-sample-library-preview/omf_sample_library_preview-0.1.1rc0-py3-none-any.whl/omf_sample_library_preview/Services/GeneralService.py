from ..Client.OMFClient import OMFClient
from ..Models.OMFContainer import OMFContainer
from ..Models.OMFData import OMFData
from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType
from ..Models.OMFType import OMFType
from .ContainerService import ContainerService
from .DataService import DataService
from .TypeService import TypeService


class GeneralService:
    def __init__(self, omf_client: OMFClient):
        self.__omf_client = omf_client
        self.__container_service = ContainerService(omf_client)
        self.__data_service = DataService(omf_client)
        self.__type_service = TypeService(omf_client)

    @property
    def OMFClient(self) -> OMFClient:
        return self.__omf_client

    @property
    def ContainerService(self) -> ContainerService:
        return self.__container_service

    @property
    def DataService(self) -> DataService:
        return self.__data_service

    @property
    def TypeService(self) -> TypeService:
        return self.__type_service

    @staticmethod
    def __split_omf_objects(
        omf_objects: list[OMFType | OMFContainer | OMFData],
    ) -> (list[OMFType], list[OMFContainer], list[OMFData]):
        types = []
        containers = []
        data = []
        for omf_object in omf_objects:
            if isinstance(omf_object, OMFType):
                types.append(omf_object)
            elif isinstance(omf_object, OMFContainer):
                containers.append(omf_object)
            elif isinstance(omf_object, OMFData):
                data.append(omf_object)
            else:
                raise TypeError('Invalid OMF Object type')

        return types, containers, data

    def create(self, omf_objects: list[OMFType | OMFContainer | OMFData]):
        """
        Creates OMF Objects and throws error on failure
        :param omf_objects: List of OMF Objects
        """
        types, containers, data = self.__split_omf_objects(omf_objects)
        if len(types) > 0:
            self.TypeService.createTypes(types)
        if len(containers) > 0:
            self.ContainerService.createContainers(containers)
        if len(data) > 0:
            self.DataService.createData(data)

    def update(self, omf_objects: list[OMFType | OMFContainer | OMFData]):
        """
        Updates OMF Objects and throws error on failure
        :param omf_objects: List of OMF Objects
        """
        types, containers, data = self.__split_omf_objects(omf_objects)
        if len(types) > 0:
            self.TypeService.updateTypes(types)
        if len(containers) > 0:
            self.ContainerService.updateContainers(containers)
        if len(data) > 0:
            self.DataService.updateData(data)

    def delete(self, omf_objects: list[OMFType | OMFContainer | OMFData]):
        """
        Deletes OMF Objects and throws error on failure
        :param omf_objects: List of OMF Objects
        """
        types, containers, data = self.__split_omf_objects(omf_objects)
        if len(types) > 0:
            self.TypeService.deleteTypes(types)
        if len(containers) > 0:
            self.ContainerService.deleteContainers(containers)
        if len(data) > 0:
            self.DataService.deleteData(data)
