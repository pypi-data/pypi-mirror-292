from typing import Dict


def Model(cls):
    """
    A models decorator that allows for the creation of a models class that is also a dictionary.
    :param cls:
    :return: class instance
    """

    class _Model(cls, Dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            dict.__init__(self, *args, **kwargs)

    return _Model
