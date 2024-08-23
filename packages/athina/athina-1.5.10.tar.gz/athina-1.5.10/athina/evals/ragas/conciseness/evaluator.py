from athina.interfaces.model import Model
from ..ragas_evaluator import RagasEvaluator
from athina.evals.eval_type import RagasEvalTypeId
from athina.metrics.metric_type import MetricType
from ragas.metrics.critique import conciseness
from typing import List, Optional

"""
RAGAS Conciseness Docs: https://docs.ragas.io/en/latest/concepts/metrics/critique.html
RAGAS Conciseness Github: https://github.com/explodinggradients/ragas/blob/main/src/ragas/metrics/critique.py
"""
class RagasConciseness(RagasEvaluator):
    """
    This evaluates if the generated llm response conveys information or ideas clearly and efficiently, without unnecessary or redundant details
    """
    @property
    def name(self):
        return RagasEvalTypeId.RAGAS_CONCISENESS.value

    @property
    def display_name(self):
        return "Ragas Conciseness"

    @property
    def metric_ids(self) -> List[str]:
        return [MetricType.RAGAS_CONCISENESS.value]
    
    @property
    def ragas_metric(self):
        return conciseness
    
    @property
    def ragas_metric_name(self):
        return "conciseness"

    @property
    def default_model(self):
        return Model.GPT35_TURBO.value

    @property
    def required_args(self):
        return ["response"]

    @property
    def examples(self):
        return None
    
    @property
    def grade_reason(self) -> str:
        return "This is calculated by how efficiently generated llm response conveys information or ideas clearly and efficiently, without unnecessary or redundant details"

    def is_failure(self, score) -> Optional[bool]:
        return bool(score < self._failure_threshold) if self._failure_threshold is not None else None
        
    def generate_data_to_evaluate(self, response, **kwargs) -> dict:
        """
        Generates data for evaluation.
        :param response: llm response
        :return: A dictionary with formatted data for evaluation.
        """
        data = {
            "contexts": [[""]],
            "question": [""],
            "answer": [response]
        }
        return data
