from ..Client.OMFClient import OMFClient
from ..Models.OMFData import OMFData
from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType


class DataService:
    def __init__(self, omf_client: OMFClient):
        self.__omf_client = omf_client

    @property
    def OMFClient(self) -> OMFClient:
        return self.__omf_client

    def createData(self, omf_data: list[OMFData]):
        """
        Creates OMF Data and throws error on failure
        :param omf_data: List of OMF Data
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Data,
            OMFMessageAction.Create,
            omf_data,
        )
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to create data')

    def updateData(self, omf_data: list[OMFData]):
        """
        Updates OMF Data and throws error on failure
        :param omf_data: List of OMF Data
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Data,
            OMFMessageAction.Update,
            omf_data,
        )
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to update data')

    def deleteData(self, omf_data: list[OMFData]):
        """
        Deletes OMF Data and throws error on failure
        :param omf_data: List of OMF Data
        """
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Data,
            OMFMessageAction.Delete,
            omf_data,
        )
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to delete data')
