from franklin_fastapi_extension import DTO
import re


@DTO
class MockDTO:
    """
    This DTO is used to test the request and response of the router
    """
    message: str


@DTO
class ValidationTest:
    """
    This DTO is used to test validation dictionary and feature of DTO
    """
    message: str

    VALIDATIONS = {
        # this will validate that the message is a string and only contains alphabets
        'message': re.compile(r'^[a-zA-Z]+$')
    }
