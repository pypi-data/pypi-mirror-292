from .factories import *
from fastapi import Request
from fastapi.responses import JSONResponse
from .models import Response, DTO


def _handle_errors(result: Response) -> JSONResponse:
    """
    A helper function to handle the errors in the Response object
    :param result: The Response object to handle
    :return: JSONResponse
    """
    if result is None:
        return not_found_response()
    elif result.errors:
        return create_response(result, 'internal_server_error')
    else:
        return success_response(result)


async def get_all(supplier: callable) -> JSONResponse:
    """
    A Helper function to handle the get all for the service handling any errors
    :param supplier: The service function to call which returns a Response object
    :return: JSONResponse
    """
    result = supplier()

    return _handle_errors(result)


async def get_by_params(function: callable, params: any) -> JSONResponse:
    """
    A helper function to handle requests with parameters. Must be used with the await keyword.
    :param function: A callable function that takes in the parameters as a parameter
    :param params: The parameters to pass to the function
    :return: JSONResponse
    """
    if params:
        result = function(params)
        return _handle_errors(result)
    else:
        return bad_request_response()


async def call(function: callable, body: Request | dict | str | int, dtoClass: DTO = None) -> JSONResponse:
    """
    A helper function to handle requests with request body validation. Must be used with the await keyword.
    :param function: A callable function that takes in the classType as a parameter
    :param body: The request body, which will be validated against the classType
    :param dtoClass: The DTO class to validate the request body against
    :return: JSONResponse
    """

    errors = None
    data = body

    if dtoClass:
        data = await body.json()
        data = dtoClass(**data)

        errors = dtoClass.validate(data)

    if not errors:
        result = function(data)
        return _handle_errors(result)
    else:
        return bad_request_response(Response(errors=errors))

