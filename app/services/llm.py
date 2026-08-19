"""
Serviço LLM unificado (Ollama / OpenAI).

Permite alternar entre provedores de LLM via variável de ambiente
`LLM_PROVIDER` no arquivo .env:

    LLM_PROVIDER=ollama   # padrão (gratuito, local)
    LLM_PROVIDER=openai   # pago (requer OPENAI_API_KEY)

O Ollama expõe uma API compatível com OpenAI no endpoint
`/v1/chat/completions`, enquanto a OpenAI também oferece a API
`Responses` (`/v1/responses`). Este serviço usa o método adequado
para cada provedor:

    - Ollama: client.chat.completions.create(...)
    - OpenAI: client.responses.create(...)
"""

import json

from openai import OpenAI

from app.core.config import settings
from app.core.constants import VALID_CATEGORIES, VALID_PRIORITIES
from app.schemas import TicketClassification


class LLMService:
    """
    Serviço de inferência de LLM com suporte a Ollama e OpenAI.

    O provedor ativo é definido por `settings.LLM_PROVIDER`:
        - "ollama": usa o servidor local Ollama (gratuito)
        - "openai": usa a API da OpenAI (requer chave de API)

    Uso:
        llm = LLMService()
        resposta = llm.responder("Explique o que é HTTP 500.")
    """

    def __init__(self) -> None:
        self.provider = settings.LLM_PROVIDER.lower()
        self._client = self._create_client()
        self.model = self._resolve_model()

    def _create_client(self) -> OpenAI:
        """Cria o cliente OpenAI configurado para o provedor ativo."""
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError(
                    "LLM_PROVIDER=openai exige OPENAI_API_KEY definida no .env"
                )
            return OpenAI(api_key=settings.OPENAI_API_KEY)

        if self.provider == "ollama":
            return OpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama",  # valor obrigatório pelo SDK, mas ignorado pelo Ollama
            )

        raise ValueError(
            f"LLM_PROVIDER inválido: '{settings.LLM_PROVIDER}'. "
            "Use 'ollama' ou 'openai'."
        )

    def _resolve_model(self) -> str:
        """Retorna o modelo ativo conforme o provedor configurado."""
        if self.provider == "openai":
            return settings.OPENAI_MODEL
        return settings.OLLAMA_MODEL

    def responder(self, prompt: str) -> str:
        """
        Envia um prompt para o modelo ativo e retorna a resposta em texto.

        Usa o endpoint correto conforme o provedor:
            - Ollama: Chat Completions (`/v1/chat/completions`)
            - OpenAI: Responses (`/v1/responses`)

        Args:
            prompt: Texto de entrada enviado ao modelo.

        Returns:
            Texto gerado pelo modelo.

        Raises:
            OpenAIError: Se a API do provedor falhar.
        """
        if self.provider == "ollama":
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content

        # OpenAI (provedor padrão da API)
        response = self._client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text

    def _build_classification_prompt(self, description: str) -> str:
        """
        Constrói o prompt que instrui o modelo a classificar um chamado.

        O prompt define o contrato de saída (JSON), os valores válidos de
        categoria e prioridade, e um exemplo concreto de resposta.
        """
        categorias = ", ".join(sorted(VALID_CATEGORIES))
        prioridades = ", ".join(sorted(VALID_PRIORITIES))

        return (
            "Você é um classificador de chamados de suporte técnico.\n"
            "Analise a descrição do chamado e classifique-o.\n\n"
            "Responda APENAS com um JSON válido, sem texto adicional, "
            "no seguinte formato (contrato obrigatório):\n"
            "{\n"
            '  "title": "título curto e descritivo",\n'
            '  "category": "uma das categorias válidas",\n'
            '  "priority": "uma das prioridades válidas"\n'
            "}\n\n"
            f"Categorias válidas: {categorias}\n"
            f"Prioridades válidas: {prioridades}\n\n"
            "Regras:\n"
            "- O título deve ter no máximo 200 caracteres.\n"
            "- A categoria deve ser uma das categorias válidas listadas.\n"
            "- A prioridade deve ser uma das prioridades válidas listadas, "
            "considerando impacto e urgência.\n\n"
            "Exemplo de resposta para a descrição "
            '"A API de pagamentos está retornando erro 500.":\n'
            "{\n"
            '  "title": "API de pagamentos retornando erro 500",\n'
            '  "category": "Financeiro",\n'
            '  "priority": "Crítica"\n'
            "}\n\n"
            f"Descrição do chamado:\n{description}\n"
        )

    def _extract_json(self, raw_response: str) -> dict:
        """
        Extrai um objeto JSON estruturado da resposta do modelo.

        O modelo pode retornar o JSON de várias formas:
            - JSON puro: `{"title": "...", ...}`
            - JSON em bloco de código markdown: ```json {...} ```
            - JSON com texto antes/depois: `Aqui está: {...}`
            - JSON com quebras de linha e espaços extras

        Args:
            raw_response: Texto bruto retornado pelo modelo.

        Returns:
            Dict com os campos estruturados do JSON.

        Raises:
            ValueError: Se não for possível extrair um objeto JSON válido.
        """
        texto = raw_response.strip()

        # 1. Tenta parsear diretamente
        try:
            data = json.loads(texto)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        # 2. Tenta extrair de bloco de código markdown (```json ... ```)
        import re

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        # 3. Tenta extrair o primeiro objeto JSON entre { e }
        inicio = texto.find("{")
        fim = texto.rfind("}")
        if inicio != -1 and fim != -1 and fim > inicio:
            try:
                data = json.loads(texto[inicio : fim + 1])
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        raise ValueError(
            "O modelo não retornou um JSON estruturado válido. "
            f"Resposta recebida: {raw_response[:200]!r}"
        )

    def classificar_ticket(self, description: str) -> TicketClassification:
        """
        Classifica um chamado via LLM e retorna o resultado estruturado.

        Envia a descrição ao modelo com o contrato `TicketClassification`
        (title, category, priority), extrai o JSON estruturado da resposta
        e valida/normaliza os valores contra os domínios da aplicação.

        Args:
            description: Texto livre do chamado.

        Returns:
            TicketClassification com title, category e priority canônicos.

        Raises:
            ValueError: Se o modelo não retornar JSON estruturado válido
                ou campos fora do domínio.
            OpenAIError: Se a API do provedor falhar.
        """
        prompt = self._build_classification_prompt(description)
        raw_response = self.responder(prompt).strip()

        data = self._extract_json(raw_response)

        if not isinstance(data, dict):
            raise ValueError(
                "O modelo deve retornar um objeto JSON com os campos "
                "title, category e priority."
            )

        return TicketClassification(**data)

    @property
    def provider_ativo(self) -> str:
        """Nome do provedor atualmente ativo."""
        return self.provider

    @property
    def modelo_ativo(self) -> str:
        """Nome do modelo atualmente ativo."""
        return self.model


# Instância singleton para uso na aplicação
llm_service = LLMService()