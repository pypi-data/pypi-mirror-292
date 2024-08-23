from dataclasses import dataclass, asdict


@dataclass
class Response:
    """
    A Response object that will be returned by the service classes

    The Response object contains two fields:
        node: the data that will be returned by the router
        errors: a list of errors that will be returned by the router

    The Response object also contains a method dict() that will return the object as a dictionary
    """
    node: any
    errors: list

    def __init__(self, node=None, errors=None):
        self.node = node
        self.errors = errors

    def dict(self):
        return asdict(self)
