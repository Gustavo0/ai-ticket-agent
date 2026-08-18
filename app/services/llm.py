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

from openai import OpenAI

from app.core.config import settings


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