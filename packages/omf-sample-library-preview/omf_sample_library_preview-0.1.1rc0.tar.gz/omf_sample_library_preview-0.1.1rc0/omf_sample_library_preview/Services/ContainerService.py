from ..Client.OMFClient import OMFClient
from ..Models.OMFContainer import OMFContainer
from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType


class ContainerService:
    def __init__(self, omf_client: OMFClient):
        self.__omf_client = omf_client

    @property
    def OMFClient(self) -> OMFClient:
        return self.__omf_client

    def createContainers(self, omf_containers: list[OMFContainer]):
        """
        Creates OMF Containers and throws error on failure
        :param omf_containers: List of OMF Containers
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Container,
            OMFMessageAction.Create,
            omf_containers,
        )
        self.__omf_client.verifySuccessfulResponse(
            response, 'Failed to create container'
        )

    def updateContainers(self, omf_containers: list[OMFContainer]):
        """
        Updates OMF Containers and throws error on failure
        :param omf_containers: List of OMF Containers
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Container,
            OMFMessageAction.Update,
            omf_containers,
        )
        self.__omf_client.verifySuccessfulResponse(
            response, 'Failed to update container'
        )

    def deleteContainers(self, omf_containers: list[OMFContainer]):
        """
        Deletes OMF Containers and throws error on failure
        :param omf_containers: List of OMF Containers
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Container,
            OMFMessageAction.Delete,
            omf_containers,
        )
        self.__omf_client.verifySuccessfulResponse(
            response, 'Failed to delete container'
        )
