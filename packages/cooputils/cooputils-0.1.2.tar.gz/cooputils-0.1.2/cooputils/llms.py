from pydantic import BaseModel
from openai import OpenAI
from cooputils.config import internal_get_loaded_config
import instructor
from typing import TypeVar, Union, Type, Dict, Any, Callable
from functools import wraps
import requests

OPENAI_CLIENT: OpenAI | None = None
INSTRUCTOR_CLIENT: instructor.Instructor | None = None

DEFAULT_MODEL = "gpt-4o-2024-08-06"


def get_openai_client():
    global OPENAI_CLIENT
    if OPENAI_CLIENT is None:
        OPENAI_CLIENT = OpenAI(api_key=internal_get_loaded_config().OPENAI_API_KEY)
    return OPENAI_CLIENT


def get_instructor_client():
    global INSTRUCTOR_CLIENT
    if INSTRUCTOR_CLIENT is None:
        INSTRUCTOR_CLIENT = instructor.from_openai(get_openai_client())
    return INSTRUCTOR_CLIENT


def chat_completion(system_prompt, user_prompt) -> str:
    completion = get_openai_client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return completion.choices[0].message.content


def local_chat_completion(system_prompt, user_prompt) -> str:
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/chat", json=payload).json()

    return response["message"]["content"]


TCompletionResponseModel = TypeVar("TCompletionResponseModel", bound=Union[BaseModel, "Iterable[Any]", "Partial[Any]"])


def structured_completion(
        system_prompt: str, user_prompt: str, response_model: type[TCompletionResponseModel],
        model: str = None, extra_parameters: Dict[str, Any] = None
) -> TCompletionResponseModel:
    if model is None:
        model = DEFAULT_MODEL

    if extra_parameters is None:
        extra_parameters = {}

    response = get_instructor_client().chat.completions.create(
        model=model,
        response_model=response_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **extra_parameters,
    )

    return response
