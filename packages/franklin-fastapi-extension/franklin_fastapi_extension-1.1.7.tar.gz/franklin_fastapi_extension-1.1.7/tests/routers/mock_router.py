from franklin_fastapi_extension import GET, POST, PUT, Query
import request
from .mock_dto import MockDTO, ValidationTest
from .mock_service import get_all, post_request

"""
This is the mock router that will be used to test the library

The file name is used to determine the prefix of the routes
The methods are used to determine the suffix of the routes

The methods should be decorated with the appropriate method decorator

All methods should be async and use the request functions to call the service methods

The request functions will handle the response and return the appropriate response object
"""


@GET("/get")
async def get_mock_router():
    """
    This is the Test GET method
    :return: Response (node= 'GET Method', errors=[])
    """

    return await request.get_all(get_all)


@POST("/post")
async def post_mock_router(mock_dto: Query):
    """
    This is the Test POST method
    :param mock_dto: {"message": "POST method"}
    :return: Response (node= {"message": "POST method"}, errors=[])
    """
    return await request.call(post_request, mock_dto, MockDTO)

@POST("/post/validate")
async def post_mock_router_validate(mock_dto: Query):
    """
    This is the Test POST method with dto validation
    this dto only accepts alphabets
    :param mock_dto: {"message": "?"}
    :return: Response (node= None, errors=["Invalid type for message: expected str, got int"])
    """
    return await request.call(post_request, mock_dto, ValidationTest)


@PUT("/put")
async def put_mock_router(mock_dto: Query):
    """
    This is the Test PUT method
    mainly just to test proof of concept for the other types of routes
    :param mock_dto: {"message": "PUT method"}
    :return:  Response (node= {"message": "PUT method"}, errors=[])
    """
    return await request.call(post_request, mock_dto, MockDTO)

