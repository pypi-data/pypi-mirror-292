from typing import TypeVar

from .raw_api.types import Response

T = TypeVar("T")

def get_body_and_handle_err(response: Response[T]) -> T:
    if response.status_code != 200:
        raise Exception(f"Status code={response.status_code}, content={response.content.decode()}")
    if response.parsed is None:
        raise Exception(f"Error parsing response")
    return response.parsed
