from typing import Protocol, List, Union
from pydantic import BaseModel

from dingo.model.modelres import ModelRes


class BaseRule(Protocol):

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        ...
