import pytest
from requests import Response

from ..Client.OMFClient import OMFClient
from ..Client.OMFError import OMFError


@pytest.fixture
def client():
    return OMFClient(url='https://test.com/omf')


def test_check_response_OK_response(client: OMFClient):
    response = Response()
    response.status_code = 200
    client.verifySuccessfulResponse(response=response, main_message='Testing')


def test_check_response_error_response(client: OMFClient):
    response = Response()

    response.status_code = 300
    response._content = b"Error"
    with pytest.raises(OMFError):
        client.verifySuccessfulResponse(response=response, main_message='Testing')

    response.status_code = 199
    response._content = b"Error"
    with pytest.raises(OMFError):
        client.verifySuccessfulResponse(response=response, main_message='Testing')


def test_invalid_omf_message_in_request_raises_error(client: OMFClient):
    with pytest.raises(TypeError):
        client.omfRequest(None, None, 'bad')
