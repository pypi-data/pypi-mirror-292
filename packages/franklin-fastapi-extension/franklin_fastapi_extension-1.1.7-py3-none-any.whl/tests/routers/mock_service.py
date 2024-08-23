from franklin_fastapi_extension import Response
from .mock_dto import MockDTO


"""
This is my mock service that will be used to test the router
This serves as an example of how the service classes should be implemented when using this library

The service class should be a class that contains the methods that will be called by the router
Each method should return a Response object

The Response object contains two fields:
    node: the data that will be returned by the router
    errors: a list of errors that will be returned by the router
    
The Response object also contains a method dict() that will return the object as a dictionary

The service class should be imported by the router and the methods should be called using the request functions
"""


# just returns the dto as is
def post_request(dto: MockDTO) -> Response:
    return Response(node=dto, errors=None)


# just returns a message
def get_all() -> Response:
    return Response(node={"message": "GET method"}, errors=None)

