# %%
import inspect
import json
import time
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Type,
    Union,
    overload,
)

import litellm
from loguru import logger
from neat.config import STRUCTURED_OUTPUT_MODELS, UNSUPPORTED_TOOL_MODELS, settings
from neat.database import load_prompt, save_execution, save_prompt
from neat.exceptions import (
    IncompatibleArgumentsError,
    TemperatureRangeError,
    UnsupportedModelFeaturesError,
)
from neat.models import ExecutionData, Message, PromptData
from neat.types import LLMModels, T
from neat.utils import generate_output_schema, hash
from pydantic import ValidationError

litellm.set_verbose = False
litellm.drop_params = True
litellm.add_function_to_prompt = False


class Neat:
    def __init__(self):
        self.registered_tools: Dict[str, Dict[str, Any]] = {}

    def _validate_inputs(
        self,
        model: str,
        temp: float,
        tools: List[Callable],
        response_model: Type[T] | None,
    ):
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 1:
            raise TemperatureRangeError("Temperature must be a float between 0 and 1")

        if any(model.lower().startswith(m) for m in UNSUPPORTED_TOOL_MODELS):
            if tools or response_model:
                raise UnsupportedModelFeaturesError(
                    f"Tool calling or structured outputs are not supported for the {model} model."
                )

        if tools and response_model:
            raise IncompatibleArgumentsError(
                "Cannot set both 'tools' and 'response_model'. Please choose one or the other."
            )

    def tool(self, name: str | None = None, description: str | None = None):
        def decorator(func: Callable):
            tool_name = name or func.__name__
            tool_description = description or func.__doc__

            if tool_name in self.registered_tools:
                logger.warning(
                    f"Tool '{tool_name}' is already registered. Overwriting."
                )

            try:
                parameters = litellm.utils.function_to_dict(func)["parameters"]
            except Exception as e:
                logger.warning(f"Error using litellm.utils.function_to_dict: {e}")
                logger.warning("Falling back to basic parameter extraction.")

                signature = inspect.signature(func)
                parameters = {
                    "type": "object",
                    "properties": {
                        name: {"type": "string"} for name in signature.parameters
                    },
                    "required": [
                        name
                        for name, param in signature.parameters.items()
                        if param.default == inspect.Parameter.empty
                    ],
                }

            self.registered_tools[tool_name] = {
                "function": func,
                "description": tool_description,
                "parameters": parameters,
            }
            return func

        return decorator

    @overload
    def lm(
        self,
        model: LLMModels = ...,
        temperature: float = ...,
        tools: List[Callable] = ...,
        response_model: None = None,
        use_db: bool = ...,
        max_iterations: int = ...,
    ) -> Callable[[Callable[..., List[Message]]], Callable[..., Any]]: ...

    @overload
    def lm(
        self,
        model: LLMModels = ...,
        temperature: float = ...,
        tools: List[Callable] = ...,
        response_model: Type[T] = ...,
        use_db: bool = ...,
        max_iterations: int = ...,
    ) -> Callable[[Callable[..., List[Message]]], Callable[..., T]]: ...

    def lm(
        self,
        model: LLMModels = settings.default_model,
        temperature: float = settings.default_temperature,
        tools: List[Callable] = [],
        response_model: Type[T] | None = None,
        use_db: bool = False,
        max_iterations: int = 20,
    ) -> T | Callable[[Callable[..., List[Message]]], Callable[..., Union[T, Any]]]:
        self._validate_inputs(model, temperature, tools, response_model)

        def decorator(
            func: Callable[..., List[Message]],
        ) -> Callable[..., Union[T, Any]]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Union[T, Any]:
                func_name = func.__name__

                if use_db:
                    # Database-related operations
                    closure = inspect.getclosurevars(func)
                    env_repr = {
                        "nonlocals": {
                            k: v
                            for k, v in closure.nonlocals.items()
                            if not k.startswith("__")
                        },
                        "globals": {
                            k: v
                            for k, v in closure.globals.items()
                            if not k.startswith("__") and k != "ell"
                        },
                    }

                    func_hash = hash(inspect.getsource(func))
                    env_hash = hash(json.dumps(env_repr, sort_keys=True))
                    version_hash = hash(func_hash + env_hash)

                    existing_prompt = load_prompt(func_name)

                    if not existing_prompt or existing_prompt.hash != version_hash:
                        new_version = (
                            (existing_prompt.version + 1) if existing_prompt else 1
                        )

                        messages = func(*args, **kwargs)
                        prompt_content = json.dumps(
                            [
                                m.model_dump(exclude_none=True, exclude_unset=True)
                                for m in messages
                            ]
                        )

                        prompt_data = PromptData(
                            func_name=func_name,
                            version=new_version,
                            hash=version_hash,
                            model=model,
                            temperature=temperature,
                            prompt=prompt_content,
                            environment=json.dumps(env_repr, default=str),
                        )
                        prompt_id = save_prompt(prompt_data)
                        logger.info(
                            f"New prompt version created for '{func_name}': v{new_version}"
                        )
                    else:
                        logger.info(
                            f"Using existing prompt version for '{func_name}': v{existing_prompt.version}"
                        )
                        prompt_data = existing_prompt
                        prompt_id = prompt_data.id

                    current_version = prompt_data.version
                    messages = [Message(**m) for m in json.loads(prompt_data.prompt)]
                else:
                    # If not using database, just call the function
                    messages = func(*args, **kwargs)

                # Format tools for litellm
                tool_definitions = []
                if tools and not response_model:
                    for tool in tools:
                        tool_name = tool.__name__
                        logger.debug(f"Preparing tool: '{tool_name}'")
                        if tool_name in self.registered_tools:
                            tool_definitions.append(
                                {
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "description": self.registered_tools[tool_name][
                                            "description"
                                        ],
                                        "parameters": self.registered_tools[tool_name][
                                            "parameters"
                                        ],
                                    },
                                }
                            )
                        else:
                            logger.warning(
                                f"Tool '{tool_name}' is not registered. Skipping."
                            )

                start_time = time.time()
                total_prompt_tokens = 0
                total_completion_tokens = 0
                try:
                    for iteration in range(max_iterations):
                        logger.debug(
                            f"Starting iteration {iteration + 1}/{max_iterations}"
                        )
                        api_params = {
                            "model": model,
                            "messages": [
                                m.model_dump(exclude_none=True, exclude_unset=True)
                                for m in messages
                            ],
                            "temperature": temperature,
                        }

                        # Adding tools if provided, setting tool choice to auto
                        if tool_definitions:
                            api_params["tools"] = tool_definitions
                            api_params["tool_choice"] = "auto"

                        # Add response_model if provided
                        if response_model:
                            if model in STRUCTURED_OUTPUT_MODELS:
                                api_params["response_format"] = response_model
                            else:
                                api_params["tools"] = [
                                    {
                                        "type": "function",
                                        "function": generate_output_schema(
                                            response_model
                                        ),
                                    }
                                ]
                                api_params["tool_choice"] = {
                                    "type": "function",
                                    "function": {
                                        "name": response_model.__name__,
                                    },
                                }
                                api_params["messages"].append(
                                    {"role": "user", "content": "Please output json"}
                                )

                        response = litellm.completion(**api_params)
                        total_prompt_tokens += response.usage.prompt_tokens
                        total_completion_tokens += response.usage.completion_tokens

                        response_message = response.choices[0].message

                        if not response_message.tool_calls:
                            final_content = response_message.content
                            logger.info(f"Completed after {iteration + 1} iterations")
                            break
                        if response_model:
                            try:
                                final_content = json.loads(
                                    response_message.tool_calls[0].function.arguments
                                )

                                return response_model.model_validate(final_content)
                            except json.JSONDecodeError as e:
                                logger.error(f"Error decoding JSON response: {e}")
                                raise
                            except ValidationError as e:
                                logger.error(f"Error validating response model: {e}")
                                raise

                        messages.append(Message(**response_message.model_dump()))
                        for tool_call in response_message.tool_calls:
                            function_name = str(tool_call.function.name)
                            function_args = json.loads(tool_call.function.arguments)

                            if function_name in self.registered_tools:
                                function_to_call = self.registered_tools[function_name][
                                    "function"
                                ]
                                try:
                                    logger.debug(
                                        f"Calling function '{function_to_call.__name__}' with args: {function_args}"
                                    )
                                    function_response = function_to_call(
                                        **function_args
                                    )
                                    logger.debug(
                                        f"Function result: {function_response}"
                                    )
                                except Exception as e:
                                    function_response = (
                                        f"Error executing {function_name}: {str(e)}"
                                    )
                                    logger.error(
                                        f"Error in function call: {function_response}"
                                    )

                                messages.append(
                                    Message(
                                        tool_call_id=tool_call.id,
                                        role="tool",
                                        name=function_name,
                                        content=str(function_response),
                                    )
                                )
                    else:
                        logger.warning(
                            f"Reached maximum iterations ({max_iterations}) without resolution"
                        )

                    execution_time = time.time() - start_time

                    if use_db:
                        execution_data = ExecutionData(
                            version_id=prompt_id,
                            prompt_tokens=total_prompt_tokens,
                            completion_tokens=total_completion_tokens,
                            execution_time=execution_time,
                        )
                        save_execution(execution_data)

                    if response_model:
                        try:
                            if model in STRUCTURED_OUTPUT_MODELS:
                                final_content = json.loads(final_content)
                            return response_model.model_validate(final_content)
                        except ValidationError as e:
                            logger.error(f"Error parsing response: {str(e)}")
                            raise

                    return final_content

                except Exception as e:
                    logger.error(f"Error in LLM completion: {str(e)}")
                    raise

            return wrapper

        return decorator

    @staticmethod
    def system(content: str) -> Message:
        return Message(role="system", content=content)

    @staticmethod
    def user(content: str) -> Message:
        return Message(role="user", content=content)

    @staticmethod
    def assistant(content: str) -> Message:
        return Message(role="assistant", content=content)


neat = Neat()
