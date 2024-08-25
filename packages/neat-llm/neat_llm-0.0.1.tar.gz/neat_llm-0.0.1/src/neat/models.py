from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExecutionData(BaseModel):
    version_id: int
    prompt_tokens: int
    completion_tokens: int
    execution_time: float

    model_config = ConfigDict(extra="forbid")


class PromptData(BaseModel):
    id: Optional[int] = None
    func_name: str
    version: int
    hash: str
    model: str
    temperature: float
    prompt: str
    environment: str

    model_config = ConfigDict(extra="forbid")


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: FunctionCall


class Message(BaseModel):
    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    tool_calls: Optional[list[ToolCall]] = None
    tool_call_id: Optional[str] = None

    model_config = {
        "extra": "allow",
        "json_schema_extra": {
            "examples": [
                {"role": "user", "content": "Hello, how are you?"},
                {
                    "role": "assistant",
                    "content": "I'm doing well, thank you for asking!",
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "arguments": '{"location": "New York"}',
                            },
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_abc123",
                    "name": "get_weather",
                    "content": "The weather in New York is sunny with a high of 75°F.",
                },
            ]
        },
    }
