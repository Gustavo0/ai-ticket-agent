"""
Testes do serviço LLM unificado (Ollama / OpenAI).

Usa mocks para não depender de servidor externo real.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.core.config import Settings
from app.services.llm import LLMService


class TestLLMService:
    """Testes do LLMService."""

    def test_provider_ollama_padrao(self):
        """Provedor padrão deve ser 'ollama'."""
        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="ollama")), \
             patch("app.services.llm.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            service = LLMService()
            assert service.provider == "ollama"
            assert service.model == "llama3.2"
            mock_openai.assert_called_once_with(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )

    def test_provider_openai(self):
        """Provedor 'openai' deve usar chave de API e modelo configurado."""
        with patch(
            "app.services.llm.settings",
            new=Settings(LLM_PROVIDER="openai", OPENAI_API_KEY="sk-teste"),
        ), patch("app.services.llm.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            service = LLMService()
            assert service.provider == "openai"
            assert service.model == "gpt-5-mini"
            mock_openai.assert_called_once_with(api_key="sk-teste")

    def test_provider_openai_sem_chave_erro(self):
        """Deve falhar se LLM_PROVIDER=openai sem OPENAI_API_KEY."""
        with patch(
            "app.services.llm.settings",
            new=Settings(LLM_PROVIDER="openai", OPENAI_API_KEY=""),
        ):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                LLMService()

    def test_provider_invalido_erro(self):
        """Deve falhar com LLM_PROVIDER inválido."""
        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="invalido")):
            with pytest.raises(ValueError, match="invalido"):
                LLMService()

    def test_responder_ollama_usar_chat_completions(self):
        """Ollama deve usar o endpoint chat.completions."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Resposta do Ollama"))]
        )

        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="ollama")), \
             patch("app.services.llm.OpenAI", return_value=mock_client):
            service = LLMService()
            resultado = service.responder("Qual é a capital do Brasil?")

            assert resultado == "Resposta do Ollama"
            mock_client.chat.completions.create.assert_called_once_with(
                model="llama3.2",
                messages=[
                    {"role": "user", "content": "Qual é a capital do Brasil?"},
                ],
            )

    def test_responder_openai_usar_responses(self):
        """OpenAI deve usar o endpoint responses.create."""
        mock_client = MagicMock()
        mock_client.responses.create.return_value = MagicMock(
            output_text="Resposta da OpenAI"
        )

        with patch(
            "app.services.llm.settings",
            new=Settings(LLM_PROVIDER="openai", OPENAI_API_KEY="sk-teste"),
        ), patch("app.services.llm.OpenAI", return_value=mock_client):
            service = LLMService()
            resultado = service.responder("Explique HTTP 500.")

            assert resultado == "Resposta da OpenAI"
            mock_client.responses.create.assert_called_once_with(
                model="gpt-5-mini",
                input="Explique HTTP 500.",
            )

    def test_properties(self):
        """Testa as propriedades provider_ativo e modelo_ativo."""
        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="ollama")), \
             patch("app.services.llm.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            service = LLMService()
            assert service.provider_ativo == "ollama"
            assert service.modelo_ativo == "llama3.2"