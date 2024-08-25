from typing import Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

LLMModels = Literal[
    "gpt-4o-mini",
    "mistral/mistral-large-latest",
    "mistral/mistral-nemo-latest",
    "gpt-4o",
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet-20240620",
    "command-r",
    "command-r-plus",
]
