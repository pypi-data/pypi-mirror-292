from dataclasses import dataclass, fields, asdict as _asDict
from typing import get_type_hints


def DTO(cls) -> object:
    """
    A DTO decorator allowing for custom validation using regex patterns.
    To use this decorator, create a class with type hints and a VALIDATIONS dictionary.
    The VALIDATIONS dictionary should contain the field name as the key and a regex pattern as the value using re.compile().
    :param cls: class to decorate
    :return: decorated class
    """

    cls = dataclass(cls)

    cls.validate = _validate

    if not hasattr(cls, 'VALIDATIONS'):
        cls.VALIDATIONS = {}

    return cls


def _validate(instance) -> list:
    """
    Validate the instance against the type hints and regex patterns defined in the class.
    :param instance: The instance to validate.
    :return: list of errors
    """

    errors = []

    # Get the type hints for the instance
    hints = get_type_hints(instance)

    # Get the fields for the instance
    instance_fields = fields(instance)

    # Iterate over the fields
    for field in instance_fields:
        field_name = field.name
        field_value = getattr(instance, field_name)

        # Check the type of the field
        if not isinstance(field_value, hints[field_name]):
            errors.append(f"Invalid type for {field_name}: expected {hints[field_name].__name__}, got {type(field_value).__name__}")
        # Check the value against regex validation if applicable
        elif field_name in instance.VALIDATIONS:
            if not instance.VALIDATIONS[field_name].match(field_value):
                errors.append(f"Invalid value for {field_name}")

    return errors


def is_dto(instance) -> bool:
    """
    Check if the instance is a DTO
    :param instance:
    :return: bool
    """
    return hasattr(instance, 'validate') and hasattr(instance, 'VALIDATIONS')


def to_dict(dto: DTO):
    """
    Convert the DTO to a dictionary
    :param dto:
    :return: dict
    """
    return _asDict(dto)