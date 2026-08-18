"""
Classificador de chamados (tickets).

Contém:
- Palavras-chave para classificação de categoria e prioridade
- Classe `TicketClassifier` para classificar textos de chamados
"""

from .structuring import TicketStructuringService

__all__ = ["TicketClassifier", "TicketStructuringService"]


class TicketClassifier:
    """
    Classificador heurístico de chamados.

    Analisa o texto da descrição e infere categoria e prioridade
    com base em palavras-chave ponderadas.
    """

    def __init__(self) -> None:
        self._structuring = TicketStructuringService()

    def classify(self, description: str) -> dict[str, str]:
        """
        Classifica uma descrição em dicionário com title, category e priority.

        Args:
            description: Texto livre do chamado.

        Returns:
            Dict com chaves `title`, `category` e `priority`.
        """
        return self._structuring.structure(description)

    def generate_title(self, description: str) -> str:
        """Gera um título a partir da descrição."""
        return self._structuring._generate_title(description)