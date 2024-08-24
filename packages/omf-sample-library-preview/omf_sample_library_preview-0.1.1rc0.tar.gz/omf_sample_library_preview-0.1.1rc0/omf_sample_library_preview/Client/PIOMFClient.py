from __future__ import annotations

import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType
from .OMFClient import OMFClient


class PIOMFClient(OMFClient):
    """Handles communication with PI OMF Endpoint."""

    def __init__(
        self,
        resource: str,
        username: str,
        password: str,
        omf_version: str = '1.2',
        logging_enabled: bool = False,
    ):
        self.__resource = resource
        self.__basic = HTTPBasicAuth(username, password)

        super().__init__(resource, omf_version, True, logging_enabled)

    def fromAppsettings(path: str = None):
        if not path:
            path = 'appsettings.json'

        try:
            with open(
                path,
                'r',
            ) as f:
                appsettings = json.load(f)
        except Exception as error:
            logging.ERROR(f'Error: {str(error)}')
            logging.ERROR(f'Could not open/read appsettings.json')
            exit()

        return PIOMFClient(
            appsettings.get('Resource'),
            appsettings.get('Username'),
            appsettings.get('Password'),
            logging_enabled=True,
        )

    @property
    def Resource(self) -> str:
        """
        Gets the base url
        :return:
        """
        return self.__resource

    def getHeaders(self, message_type: OMFMessageType, action: OMFMessageAction):
        headers = super().getHeaders(message_type, action)
        headers['x-requested-with'] = 'xmlhttprequest'
        return headers

    def request(
        self,
        method: str,
        url: str,
        params=None,
        data=None,
        headers=None,
        additional_headers=None,
        **kwargs,
    ) -> requests.Response:
        return super().request(
            method,
            url,
            params,
            data,
            headers,
            additional_headers,
            auth=self.__basic,
            **kwargs,
        )
