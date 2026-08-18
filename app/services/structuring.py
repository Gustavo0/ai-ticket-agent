"""
Serviço de estruturação de chamados.

Recebe um chamado em linguagem natural e o estrutura em campos:
título, categoria, prioridade e status.
"""

from app.core.constants import (
    CATEGORY_ALIASES,
    PRIORITY_ALIASES,
    TicketCategory,
    TicketPriority,
)


class TicketStructuringService:
    """
    Serviço responsável por receber um chamado textual e inferir
    campos estruturados (título, categoria, prioridade) a partir dele.
    """

    # Palavras-chave para inferência de categoria.
    # Palavras mais específicas têm peso maior (ex: "pagamento" = 3).
    CATEGORY_KEYWORDS: dict[str, dict[str, int]] = {
        TicketCategory.BUG.value: {
            "erro": 1, "error": 1, "bug": 3, "falha": 2, "falhou": 2,
            "exception": 3, "crash": 3, "500": 1, "404": 1,
            "retornando": 1, "não funciona": 3, "nao funciona": 3,
            "quebrou": 2, "corrompido": 2, "corrompida": 2,
            "inválido": 2, "invalido": 2, "stack trace": 3, "traceback": 3,
        },
        TicketCategory.SUPORTE.value: {
            "ajuda": 2, "help": 2, "suporte": 2, "support": 2,
            "dúvida": 2, "duvida": 2, "como": 1, "preciso de": 2,
            "acesso": 2, "senha": 3, "login": 3, "logar": 3,
            "não consigo": 3, "nao consigo": 3, "esqueci": 2,
        },
        TicketCategory.MELHORIA.value: {
            "melhorar": 2, "melhoria": 2, "improve": 2, "enhancement": 3,
            "sugestão": 3, "sugestao": 3, "gostaria de": 2,
            "seria bom": 3, "ideal seria": 3, "novo recurso": 3,
            "feature": 3, "otimizar": 2, "otimizacao": 2,
        },
        TicketCategory.FINANCEIRO.value: {
            "pagamento": 4, "pagamentos": 4, "payment": 4, "payments": 4,
            "fatura": 4, "nota fiscal": 4, "nf": 4, "boleto": 4,
            "cartão": 4, "cartao": 4, "reembolso": 4, "preço": 3,
            "preco": 3, "cobranca": 4, "cobrança": 4, "crédito": 4,
            "credito": 4, "débito": 4, "debito": 4, "pix": 4,
        },
        TicketCategory.INFRAESTRUTURA.value: {
            "servidor": 3, "server": 3, "rede": 3, "network": 3,
            "banco": 2, "database": 3, "db": 2, "disco": 3,
            "memória": 3, "memoria": 3, "cpu": 3, "processamento": 2,
            "lentidão": 2, "lentidao": 2, "down": 4, "offline": 4,
            "indisponível": 3, "indisponivel": 3, "monitoramento": 3,
            "log": 2, "logs": 2, "ssl": 3, "certificado": 3,
        },
    }

    # Palavras-chave para prioridade.
    # Palavras fortes têm peso maior.
    PRIORITY_KEYWORDS: dict[str, dict[str, int]] = {
        TicketPriority.CRITICA.value: {
            "urgente": 4, "urgência": 4, "urgência": 4, "crítico": 3,
            "critico": 3, "emergência": 4, "emergencia": 4,
            "indisponível": 3, "indisponivel": 3, "fora do ar": 4,
            "500": 3, "crash": 4, "dados perdidos": 4,
            "perda de dados": 4, "incidente": 3,
        },
        TicketPriority.ALTA.value: {
            "alta": 2, "alto": 2, "parado": 3, "bloqueado": 3,
            "bloqueando": 3, "não funciona": 3, "nao funciona": 3,
            "erro grave": 3, "afetando todos": 4, "impedindo": 3,
        },
        TicketPriority.MEDIA.value: {
            "média": 2, "médio": 2, "intermitente": 3,
            "alguns usuários": 3, "alguns usuarios": 3,
            "relatório": 2, "relatorio": 2, "atrasa": 2,
        },
        TicketPriority.BAIXA.value: {
            "baixa": 2, "baixo": 2, "menor": 2, "cosmético": 3,
            "cosmetico": 3, "estético": 3, "estetico": 3,
            "melhoria": 2, "sugestão": 3, "sugestao": 3,
            "quando puder": 3, "eventualmente": 2, "nice to have": 4,
        },
    }

    def structure(self, description: str) -> dict:
        """
        Estrutura uma descrição livre de chamado em campos.

        Args:
            description: Texto livre do chamado, ex: "A API de pagamentos está retornando erro 500."

        Returns:
            Dict com `title`, `category`, `priority` inferidos.
        """
        description = description.strip()
        title = self._generate_title(description)
        category = self._infer_category(description)
        priority = self._infer_priority(description)

        return {
            "title": title,
            "category": category,
            "priority": priority,
        }

    def _generate_title(self, description: str) -> str:
        """Gera um título conciso a partir da descrição (primeiras 10 palavras)."""
        words = description.split()
        if len(words) <= 10:
            return description
        return " ".join(words[:10]) + "..."

    def _infer_category(self, text: str) -> str | None:
        """
        Infere a categoria do chamado com base em palavras-chave.
        Palavras-chave específicas têm peso maior, evitando falsos positivos.
        """
        text_lower = text.lower()

        best_category = None
        best_score = 0

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(
                weight
                for keyword, weight in keywords.items()
                if keyword in text_lower
            )
            if score > best_score:
                best_score = score
                best_category = category

        return best_category

    def _infer_priority(self, text: str) -> str | None:
        """Infere a prioridade do chamado com base em palavras-chave."""
        text_lower = text.lower()

        best_priority = None
        best_score = 0

        # Prioridades mais altas têm precedência em caso de empate
        priority_order = (
            TicketPriority.CRITICA.value,
            TicketPriority.ALTA.value,
            TicketPriority.MEDIA.value,
            TicketPriority.BAIXA.value,
        )

        for priority in priority_order:
            keywords = self.PRIORITY_KEYWORDS[priority]
            score = sum(
                weight
                for keyword, weight in keywords.items()
                if keyword in text_lower
            )
            if score > best_score:
                best_score = score
                best_priority = priority

        return best_priority