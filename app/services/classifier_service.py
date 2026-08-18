"""
Serviço de classificação de chamados (API pública).

Expose `TicketClassifier` para uso na camada de rotas.
"""

from app.services.classifier import TicketClassifier

__all__ = ["TicketClassifier"]