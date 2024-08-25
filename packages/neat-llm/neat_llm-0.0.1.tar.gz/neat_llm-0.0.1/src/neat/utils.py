import hashlib
from functools import wraps
from typing import Any, Type

from docstring_parser import parse
from loguru import logger
from pydantic import BaseModel


def generate_output_schema(cls: Type[BaseModel]) -> dict:
    """
    Generates the schema compatible with the LLM function-call API for a given Pydantic model.

    Args:
        cls (Type[BaseModel]): The Pydantic model class to generate the schema for.

    Returns:
        dict: The schema as a dictionary.
    """
    schema = cls.model_json_schema()
    docstring = parse(cls.__doc__ or "")
    parameters = {k: v for k, v in schema.items() if k not in ("title", "description")}

    # Use docstring for the description
    description = (
        docstring.short_description
        if docstring.short_description
        else f"{cls.__name__} function"
    )

    parameters["properties"] = {
        field: details for field, details in parameters["properties"].items()
    }
    parameters["required"] = sorted(
        k for k, v in parameters["properties"].items() if "default" not in v
    )
    _recursive_purge_dict_key(parameters, "additionalProperties")
    _recursive_purge_dict_key(parameters, "title")

    return {
        "name": cls.__name__,
        "description": description,
        "parameters": parameters,
    }


def log_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper


def hash(obj: Any) -> str:
    if isinstance(obj, (str, int, float, bool, type(None))):
        return hashlib.sha256(str(obj).encode()).hexdigest()
    elif isinstance(obj, (list, tuple)):
        return hashlib.sha256(str(tuple(hash(i) for i in obj)).encode()).hexdigest()
    elif isinstance(obj, set):
        return hashlib.sha256(str(sorted(hash(i) for i in obj)).encode()).hexdigest()
    elif isinstance(obj, dict):
        return hashlib.sha256(
            str(sorted((hash(k), hash(v)) for k, v in obj.items())).encode()
        ).hexdigest()
    elif callable(obj):
        return hashlib.sha256(inspect.getsource(obj).encode()).hexdigest()
    else:
        return hashlib.sha256(str(type(obj)).encode()).hexdigest()


def _recursive_purge_dict_key(d: Any, k: str) -> None:
    """Remove a key from a dictionary recursively."""
    if isinstance(d, dict):
        keys_to_delete = [key for key, value in d.items() if key == k]
        for key in keys_to_delete:
            del d[key]
        for value in d.values():
            _recursive_purge_dict_key(value, k)
    elif isinstance(d, list):
        for item in d:
            _recursive_purge_dict_key(item, k)
