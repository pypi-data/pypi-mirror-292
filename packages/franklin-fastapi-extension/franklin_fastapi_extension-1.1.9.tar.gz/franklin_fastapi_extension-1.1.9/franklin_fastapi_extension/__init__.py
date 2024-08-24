from .models import Base
from .schemas import Response
from .utils import Database, Repository


def API(response_class=None, exception_handlers: dict=None, **kwargs):
    from config import validation_error_handler, JsonResponse, HTTPException_handler
    from fastapi import FastAPI, HTTPException
    from fastapi.exceptions import RequestValidationError
    return FastAPI(
        default_response_class=response_class or JsonResponse,
        exception_handlers=exception_handlers or {
            RequestValidationError: validation_error_handler,
            HTTPException: HTTPException_handler
        },
        **kwargs
    )
