from functools import wraps
from abc import ABC, abstractmethod
from typing import Protocol, List, Dict, Any, Union

from dingo.io import InputModel, SummaryModel


class ExecProto(Protocol):
    def load_data(self, path: str, data_type: str) -> List[InputModel]:
        ...

    def evaluate(self) -> SummaryModel:
        ...

    def summarize(self, inputs: InputModel) -> SummaryModel:
        ...

    def execute(self) -> List[SummaryModel]:
        ...


class Executor(ABC):
    exec_map: Dict[str, Any] = {}

    @abstractmethod
    def load_data(self) -> List[InputModel]:
        raise NotImplementedError()

    @abstractmethod
    def evaluate(self, *args, **kwargs) -> Union[SummaryModel, List[SummaryModel], Any]:
        raise NotImplementedError()

    @abstractmethod
    def summarize(self, record) -> SummaryModel:
        raise NotImplementedError()

    @abstractmethod
    def execute(self, *args, **kwargs) -> List[SummaryModel]:
        raise NotImplementedError()

    @classmethod
    def register(cls, exec_name: str):

        def decorator(root_exec):
            cls.exec_map[exec_name] = root_exec

            @wraps(root_exec)
            def wrapped_function(*args, **kwargs):
                return root_exec(*args, **kwargs)

            return wrapped_function

        return decorator

