"""
Classificador de chamados baseado em LLM (Llama via Ollama).

Recebe uma descrição de chamado e retorna uma estrutura Pydantic
com title, category e priority, usando structured output do Ollama.

Arquitetura:

    description
        ↓
    LLMClassifier
        ↓
    Ollama / Llama
        ↓
    resultado estruturado (JSON)
        ↓
    TicketClassification (Pydantic)
"""

from openai import OpenAI

from app.core.config import settings
from app.core.constants import VALID_CATEGORIES, VALID_PRIORITIES
from app.schemas import TicketClassification


class LLMClassifier:
    """
    Classifica chamados usando Llama via Ollama.

    Usa o modo JSON estruturado do Ollama (response_format) para
    garantir que a resposta seja um JSON válido, validado pelo
    schema Pydantic `TicketClassification`.
    """

    def __init__(self) -> None:
        self._client = OpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama",  # valor obrigatório pelo SDK, ignorado pelo Ollama
        )
        self.model = settings.OLLAMA_MODEL

    def _build_system_prompt(self) -> str:
        """
        Constrói o prompt de sistema para classificação de tickets.

        Instrui o modelo a:
        1. interpretar a descrição do usuário;
        2. gerar um título curto;
        3. identificar a categoria;
        4. determinar a prioridade;
        5. retornar somente os campos definidos pelo schema;
        6. não inventar informações que não estejam disponíveis;
        7. utilizar apenas categorias e prioridades válidas.
        """
        categorias = ", ".join(sorted(VALID_CATEGORIES))
        prioridades = ", ".join(sorted(VALID_PRIORITIES))

        return (
            "Você é um classificador de chamados de suporte técnico.\n"
            "Analise a descrição do chamado e classifique-o.\n\n"
            "Tarefas:\n"
            "1. Interprete a descrição do usuário.\n"
            "2. Gere um título curto e descritivo.\n"
            "3. Identifique a categoria.\n"
            "4. Determine a prioridade.\n\n"
            "Regras:\n"
            "- Retorne somente os campos definidos pelo schema.\n"
            "- Não invente informações que não estejam disponíveis.\n"
            "- Use apenas categorias e prioridades válidas.\n\n"
            f"Categorias válidas: {categorias}\n"
            f"Prioridades válidas: {prioridades}\n\n"
            "Responda APENAS com um JSON válido no formato:\n"
            '{"title": "...", "category": "...", "priority": "..."}\n'
        )

    def classify(self, description: str) -> TicketClassification:
        """
        Classifica uma descrição de chamado.

        Args:
            description: Texto livre do chamado.

        Returns:
            TicketClassification com title, category e priority.

        Raises:
            OpenAIError: Se a API do Ollama falhar.
            ValidationError: Se a resposta não for válida.
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": description},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return TicketClassification.model_validate_json(content)