from ..models.response import Response
from fastapi.responses import JSONResponse


"""
The Response Factory module is used to generate responses for the API

The module contains a series of functions that will generate a JSONResponse object

The functions turn the Response object along with the status code and turns it into a JSONResponse object


The functions are:
    - success_response: returns a 200 status code
    - created_response: returns a 201 status code
    - bad_request_response: returns a 400 status code
    - unauthorized_response: returns a 401 status code
    - forbidden_response: returns a 403 status code
    - not_found_response: returns a 404 status code
    - internal_server_error_response: returns a 500 status code
    - create_response: returns a JSONResponse object with the specified status code
"""

_status_codes = {
    'success': 200,
    'created': 201,
    'bad_request': 400,
    'unauthorized': 401,
    'forbidden': 403,
    'not_found': 404,
    'internal_server_error': 500,
}


def _generate_response(data: Response, status: str = 'success') -> JSONResponse:
    if status not in _status_codes:
        status = 'internal_server_error'
    if data is None:
        data = Response()

    return JSONResponse(
        content=data.dict(),
        status_code=_status_codes[status]
    )


def success_response(data: Response = None) -> JSONResponse:
    """
    :param data: Response | None
    :return: JSONResponse
    """
    return _generate_response(data, 'success')


def created_response(data: Response = None) -> JSONResponse:
    """
    :param data: Response | None
    :return: JSONResponse
    """
    return _generate_response(data, 'created')


def bad_request_response(data: Response = None) -> JSONResponse:
    """
    :param data: Response | None
    :return: JSONResponse
    """
    return _generate_response(data, 'bad_request')


def unauthorized_response(data: Response = None) -> JSONResponse:
    """
    :param data: Response | None
    :return: JSONResponse
    """
    return _generate_response(data, 'unauthorized')


def forbidden_response(data: Response = None) -> JSONResponse:
    """
    :param data: Response | None
    :return: JSONResponse
    """
    return _generate_response(data, 'forbidden')


def not_found_response(data: Response = None) -> JSONResponse:
    """
    :param data: Response | None
    :return: JSONResponse
    """
    return _generate_response(data, 'not_found')


def internal_server_error_response(data: Response = None) -> JSONResponse:
    """
    :param data: Response | None
    :return: JSONResponse
    """
    return _generate_response(data, 'internal_server_error')


def create_response(data: Response = None, status='success') -> JSONResponse:
    """
    :param data: Response | None
    :param status: must be a proper status code
    :return: JSONResponse
    """
    return _generate_response(data, status)
