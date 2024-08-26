from typing import List, Dict

from pydantic import BaseModel


class SummaryModel(BaseModel):
    dataset_id: str
    input_model: str
    input_path: str
    output_path: str
    score: float
    num_good: int
    num_bad: int
    total: int
    error_type_ratio: Dict[str, float] = {}
    error_name_ratio: Dict[str, float] = {}

    def to_dict(self):
        return {
            'dataset_id': self.dataset_id,
            'input_model': self.input_model,
            'input_path': self.input_path,
            'output_path': self.output_path,
            'score': self.score,
            'num_good': self.num_good,
            'num_bad': self.num_bad,
            'total': self.total,
            'error_type_ratio': self.error_type_ratio,
            'error_name_ratio': self.error_name_ratio,
        }


class ErrorInfo(BaseModel):
    data_id: str
    prompt: str
    content: str
    error_type: List[str] = []
    error_name: List[str] = []
    error_reason: List[str] = []

    def to_dict(self):
        return {
            'data_id': self.data_id,
            'prompt': self.prompt,
            'content': self.content,
            'error_type': self.error_type,
            'error_name': self.error_name,
            'error_reason': self.error_reason
        }