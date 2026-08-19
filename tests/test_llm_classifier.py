"""
Testes do LLMClassifier.

Separação:
- Testes unitários: não dependem de Ollama rodando (usam mocks).
- Testes de integração: exigem Ollama rodando localmente (marcados com @pytest.mark.integration).
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from app.schemas import TicketClassification
from app.services.llm_classifier import LLMClassifier


# --- Fixtures / Helpers ---


def _criar_classifier_com_resposta(resposta: str) -> LLMClassifier:
    """Cria um LLMClassifier com mock do cliente retornando `resposta`."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=resposta))]
    )
    with patch("app.services.llm_classifier.OpenAI", return_value=mock_client):
        return LLMClassifier()


# --- Testes unitários ---


class TestLLMClassifierUnit:
    """Testes unitários do LLMClassifier (sem Ollama)."""

    def test_init_usa_ollama(self):
        """Deve configurar o cliente para Ollama."""
        with patch("app.services.llm_classifier.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            classifier = LLMClassifier()

            assert classifier.model == "llama3.2"
            mock_openai.assert_called_once_with(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )

    def test_prompt_contem_instrucoes(self):
        """O prompt de sistema deve conter as instruções de classificação."""
        with patch("app.services.llm_classifier.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            classifier = LLMClassifier()

            prompt = classifier._build_system_prompt()

            assert "classificador de chamados" in prompt
            assert "título curto" in prompt
            assert "categoria" in prompt
            assert "prioridade" in prompt
            assert "não invente" in prompt.lower()
            assert "categorias válidas" in prompt.lower()
            assert "prioridades válidas" in prompt.lower()
            assert "Bug" in prompt
            assert "Suporte" in prompt
            assert "Melhoria" in prompt
            assert "Financeiro" in prompt
            assert "Infraestrutura" in prompt
            assert "Outro" in prompt
            assert "Baixa" in prompt
            assert "Média" in prompt
            assert "Alta" in prompt
            assert "Crítica" in prompt

    def test_classify_retorna_ticket_classification(self):
        """Deve retornar TicketClassification com valores canônicos."""
        resposta = json.dumps({
            "title": "VPN não conecta",
            "category": "Infraestrutura",
            "priority": "Alta",
        })

        classifier = _criar_classifier_com_resposta(resposta)
        resultado = classifier.classify("Minha VPN não quer conectar mais.")

        assert isinstance(resultado, TicketClassification)
        assert resultado.title == "VPN não conecta"
        assert resultado.category == "Infraestrutura"
        assert resultado.priority == "Alta"

    def test_classify_normaliza_aliases(self):
        """Aliases ('media', 'critica') devem ser normalizados."""
        resposta = json.dumps({
            "title": "Sistema fora do ar",
            "category": "infraestrutura",
            "priority": "critica",
        })

        classifier = _criar_classifier_com_resposta(resposta)
        resultado = classifier.classify("O sistema está fora do ar.")

        assert resultado.category == "Infraestrutura"
        assert resultado.priority == "Crítica"

    def test_classify_categoria_invalida_erro(self):
        """Categoria fora do domínio deve lançar ValidationError."""
        resposta = json.dumps({
            "title": "Título",
            "category": "CategoriaInexistente",
            "priority": "Alta",
        })

        classifier = _criar_classifier_com_resposta(resposta)
        with pytest.raises(ValidationError, match="Categoria inválida"):
            classifier.classify("Descrição do chamado")

    def test_classify_prioridade_invalida_erro(self):
        """Prioridade fora do domínio deve lançar ValidationError."""
        resposta = json.dumps({
            "title": "Título",
            "category": "Bug",
            "priority": "Extrema",
        })

        classifier = _criar_classifier_com_resposta(resposta)
        with pytest.raises(ValidationError, match="Prioridade inválida"):
            classifier.classify("Descrição do chamado")

    def test_classify_campos_ausentes_erro(self):
        """Campos obrigatórios ausentes devem lançar ValidationError."""
        resposta = json.dumps({
            "title": "Título",
            "category": "Bug",
        })

        classifier = _criar_classifier_com_resposta(resposta)
        with pytest.raises(ValidationError, match="priority"):
            classifier.classify("Descrição do chamado")

    def test_classify_resposta_nao_json_erro(self):
        """Resposta que não é JSON deve lançar ValidationError."""
        classifier = _criar_classifier_com_resposta("Isso não é JSON")
        with pytest.raises(ValidationError):
            classifier.classify("Descrição do chamado")

    def test_classify_usa_response_format_json(self):
        """Deve usar response_format json_object para structured output."""
        resposta = json.dumps({
            "title": "Título",
            "category": "Bug",
            "priority": "Alta",
        })

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=resposta))]
        )

        with patch("app.services.llm_classifier.OpenAI", return_value=mock_client):
            classifier = LLMClassifier()
            classifier.classify("Descrição do chamado")

            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs["response_format"] == {"type": "json_object"}
            assert call_kwargs["model"] == "llama3.2"

            messages = call_kwargs["messages"]
            assert messages[0]["role"] == "system"
            assert "classificador" in messages[0]["content"]
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "Descrição do chamado"


# --- Testes de integração (exigem Ollama rodando) ---


@pytest.mark.integration
class TestLLMClassifierIntegration:
    """Testes de integração com Ollama real (requer `ollama serve`)."""

    @pytest.fixture(autouse=True)
    def _verificar_ollama(self):
        """Pula o teste se Ollama não estiver rodando."""
        import socket

        try:
            with socket.create_connection(("localhost", 11434), timeout=1):
                pass
        except OSError:
            pytest.skip("Ollama não está rodando em localhost:11434")

    def test_classify_com_ollama_real(self):
        """Classifica um chamado real usando Llama via Ollama."""
        classifier = LLMClassifier()
        resultado = classifier.classify(
            "Minha VPN não quer conectar mais, aparece erro de autenticação."
        )

        assert isinstance(resultado, TicketClassification)
        assert resultado.title
        assert resultado.category in {
            "Bug", "Suporte", "Melhoria", "Financeiro", "Infraestrutura", "Outro"
        }
        assert resultado.priority in {"Baixa", "Média", "Alta", "Crítica"}
