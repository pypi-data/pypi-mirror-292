from __future__ import annotations

import json
import logging

from .OMFClient import OMFClient


class EDSOMFClient(OMFClient):
    """Handles communication with EDS OMF Endpoint."""

    def __init__(
        self,
        resource: str,
        api_version: str,
        omf_version: str = '1.2',
        logging_enabled: bool = False,
    ):
        self.__resource = resource
        self.__api_version = api_version
        self.__full_path = (
            f'{resource}/api/{api_version}/Tenants/default/Namespaces/default'
        )

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

        return EDSOMFClient(
            appsettings.get('Resource'),
            appsettings.get('ApiVersion'),
            logging_enabled=True,
        )

    @property
    def Resource(self) -> str:
        """
        Gets the base url
        :return:
        """
        return self.__resource

    @property
    def ApiVersion(self) -> str:
        """
        Returns just the base api versioning information
        :return:
        """
        return self.__api_version

    @property
    def FullPath(self) -> bool:
        return self.__full_path
