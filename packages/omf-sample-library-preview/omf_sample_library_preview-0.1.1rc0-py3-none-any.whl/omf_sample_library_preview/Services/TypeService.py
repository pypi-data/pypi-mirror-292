from ..Client.OMFClient import OMFClient
from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType
from ..Models.OMFType import OMFType


class TypeService:
    def __init__(self, omf_client: OMFClient):
        self.__omf_client = omf_client

    @property
    def OMFClient(self) -> OMFClient:
        return self.__omf_client

    def createTypes(self, omf_types: list[OMFType]):
        """
        Creates OMF Types and throws error on failure
        :param omf_types: List of OMF Types
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Type,
            OMFMessageAction.Create,
            omf_types,
        )
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to create types')

    def updateTypes(self, omf_types: list[OMFType]):
        """
        Updates OMF Types and throws error on failure
        :param omf_types: List of OMF Types
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Type,
            OMFMessageAction.Update,
            omf_types,
        )
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to update types')

    def deleteTypes(self, omf_types: list[OMFType]):
        """
        Deletes OMF Types and throws error on failure
        :param omf_types: List of OMF Types
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Type,
            OMFMessageAction.Delete,
            omf_types,
        )
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to delete types')
