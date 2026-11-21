from abc import ABC, abstractmethod
from typing import Any


class BaseQuestionPipeline(ABC):
    """Classe abstrata que define o fluxo de extração, normalização e cadastro de questões."""

    @abstractmethod
    def extract(self) -> Any:
        """Extrai as questões da base de dados de origem."""

    @abstractmethod
    def normalize(self, raw_data: Any) -> Any:
        """Normaliza e limpa ruídos dos dados extraídos."""

    @abstractmethod
    def save(self, normalized_data: Any) -> None:
        """Cadastra as questões normalizadas no banco de dados."""
