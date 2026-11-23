from abc import ABC, abstractmethod
from typing import Any

from database.repository import Exam, Question


class BaseIngestion(ABC):
    """Classe abstrata base para os processos de ingestão de questões."""

    @abstractmethod
    def extract(self) -> dict[str, Any]:
        """Extrai os dados brutos da fonte de origem."""

    @abstractmethod
    def normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normaliza os dados extraídos para o formato esperado pela persistência."""

    @abstractmethod
    def save(self, data: dict[str, Any], exam: Exam, question: Question) -> None:
        """Persiste os dados normalizados utilizando os repositórios de exame e questão."""
