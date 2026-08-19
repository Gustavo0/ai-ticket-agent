"""
Testes do serviço LLM unificado (Ollama / OpenAI).

Usa mocks para não depender de servidor externo real.
Verifica que a saída do LLM é estruturada corretamente em
`TicketClassification` (title, category, priority canônicos).
"""

import json

import pytest
from pydantic import ValidationError
from unittest.mock import patch, MagicMock

from app.core.config import Settings
from app.schemas import TicketClassification
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


class TestClassificarTicketEstruturado:
    """
    Testes de classificação estruturada via LLM.

    Verifica que a saída do LLM é convertida em `TicketClassification`
    com valores canônicos, independentemente do formato bruto retornado
    (JSON puro, markdown, texto ao redor, etc.).
    """

    # --- Helpers ---

    def _criar_service_ollama(self, resposta: str) -> LLMService:
        """Cria um LLMService com mock do Ollama retornando `resposta`."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=resposta))]
        )
        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="ollama")), \
             patch("app.services.llm.OpenAI", return_value=mock_client):
            return LLMService()

    def _criar_service_openai(self, resposta: str) -> LLMService:
        """Cria um LLMService com mock da OpenAI retornando `resposta`."""
        mock_client = MagicMock()
        mock_client.responses.create.return_value = MagicMock(
            output_text=resposta
        )
        with patch(
            "app.services.llm.settings",
            new=Settings(LLM_PROVIDER="openai", OPENAI_API_KEY="sk-teste"),
        ), patch("app.services.llm.OpenAI", return_value=mock_client):
            return LLMService()

    # --- JSON puro ---

    def test_json_puro_ollama(self):
        """JSON puro do Ollama deve ser estruturado em TicketClassification."""
        descricao = "A API de pagamentos está retornando erro 500."
        resposta = json.dumps({
            "title": "API de pagamentos retornando erro 500",
            "category": "financeiro",
            "priority": "critica",
        })

        service = self._criar_service_ollama(resposta)
        resultado = service.classificar_ticket(descricao)

        assert isinstance(resultado, TicketClassification)
        assert resultado.title == "API de pagamentos retornando erro 500"
        assert resultado.category == "Financeiro"
        assert resultado.priority == "Crítica"

    def test_json_puro_openai(self):
        """JSON puro da OpenAI deve ser estruturado em TicketClassification."""
        descricao = "Não consigo acessar o sistema com minha senha."
        resposta = json.dumps({
            "title": "Falha de acesso ao sistema",
            "category": "Suporte",
            "priority": "Alta",
        })

        service = self._criar_service_openai(resposta)
        resultado = service.classificar_ticket(descricao)

        assert isinstance(resultado, TicketClassification)
        assert resultado.title == "Falha de acesso ao sistema"
        assert resultado.category == "Suporte"
        assert resultado.priority == "Alta"

    # --- JSON em bloco de código markdown ---

    def test_json_em_bloco_markdown(self):
        """JSON dentro de bloco ```json ... ``` deve ser extraído."""
        descricao = "O servidor de banco de dados está fora do ar."
        resposta = (
            "Aqui está a classificação:\n\n"
            "```json\n"
            "{\n"
            '  "title": "Servidor de banco de dados fora do ar",\n'
            '  "category": "Infraestrutura",\n'
            '  "priority": "Crítica"\n'
            "}\n"
            "```\n"
        )

        service = self._criar_service_ollama(resposta)
        resultado = service.classificar_ticket(descricao)

        assert isinstance(resultado, TicketClassification)
        assert resultado.title == "Servidor de banco de dados fora do ar"
        assert resultado.category == "Infraestrutura"
        assert resultado.priority == "Crítica"

    def test_json_em_bloco_markdown_sem_tag_json(self):
        """JSON em bloco ``` sem a tag 'json' também deve ser extraído."""
        descricao = "Seria bom ter um relatório mensal."
        resposta = (
            "```\n"
            "{\"title\": \"Relatório mensal de chamados\", "
            "\"category\": \"Melhoria\", \"priority\": \"Baixa\"}\n"
            "```\n"
        )

        service = self._criar_service_ollama(resposta)
        resultado = service.classificar_ticket(descricao)

        assert isinstance(resultado, TicketClassification)
        assert resultado.title == "Relatório mensal de chamados"
        assert resultado.category == "Melhoria"
        assert resultado.priority == "Baixa"

    # --- JSON com texto ao redor ---

    def test_json_com_texto_antes_depois(self):
        """JSON com texto antes e depois deve ser extraído."""
        descricao = "Estou recebendo uma exception ao salvar os dados."
        resposta = (
            "Analisei o chamado. Segue a classificação:\n"
            "{\"title\": \"Exception ao salvar dados\", "
            "\"category\": \"Bug\", \"priority\": \"Alta\"}\n"
            "Espero ter ajudado!"
        )

        service = self._criar_service_ollama(resposta)
        resultado = service.classificar_ticket(descricao)

        assert isinstance(resultado, TicketClassification)
        assert resultado.title == "Exception ao salvar dados"
        assert resultado.category == "Bug"
        assert resultado.priority == "Alta"

    # --- JSON com espaços e quebras de linha extras ---

    def test_json_com_espacos_e_quebras_extras(self):
        """JSON com espaços e quebras de linha extras deve ser normalizado."""
        descricao = "O sistema está com lentidão intermitente."
        resposta = (
            "\n\n  {\n"
            '    "title": "Lentidão intermitente no sistema",\n'
            '    "category": "Suporte",\n'
            '    "priority": "Média"\n'
            "  }\n\n"
        )

        service = self._criar_service_ollama(resposta)
        resultado = service.classificar_ticket(descricao)

        assert isinstance(resultado, TicketClassification)
        assert resultado.title == "Lentidão intermitente no sistema"
        assert resultado.category == "Suporte"
        assert resultado.priority == "Média"

    # --- Normalização de valores canônicos ---

    def test_normaliza_aliases_prioridade(self):
        """Aliases de prioridade ('media', 'critica') devem ser normalizados."""
        descricao = "O sistema está fora do ar."
        resposta = json.dumps({
            "title": "Sistema fora do ar",
            "category": "Infraestrutura",
            "priority": "critica",
        })

        service = self._criar_service_ollama(resposta)
        resultado = service.classificar_ticket(descricao)

        assert resultado.priority == "Crítica"

    def test_normaliza_categoria_minuscula(self):
        """Categoria em minúsculo deve ser normalizada para canônico."""
        descricao = "A API de pagamentos está retornando erro 500."
        resposta = json.dumps({
            "title": "API de pagamentos com erro",
            "category": "financeiro",
            "priority": "Alta",
        })

        service = self._criar_service_ollama(resposta)
        resultado = service.classificar_ticket(descricao)

        assert resultado.category == "Financeiro"

    # --- Erros de estruturação ---

    def test_resposta_nao_json_erro(self):
        """Deve lançar ValueError se o modelo não retornar JSON estruturado."""
        service = self._criar_service_ollama("Isso não é JSON")
        with pytest.raises(ValueError, match="JSON estruturado"):
            service.classificar_ticket("Descrição do chamado")

    def test_resposta_lista_erro(self):
        """Deve lançar ValueError se o JSON for uma lista, não um objeto."""
        service = self._criar_service_ollama('["a", "b"]')
        with pytest.raises(ValueError, match="JSON estruturado"):
            service.classificar_ticket("Descrição do chamado")

    def test_resposta_markdown_sem_json_erro(self):
        """Bloco markdown sem JSON válido deve lançar ValueError."""
        service = self._criar_service_ollama("```\nIsso não é JSON\n```")
        with pytest.raises(ValueError, match="JSON estruturado"):
            service.classificar_ticket("Descrição do chamado")

    def test_resposta_texto_sem_chaves_erro(self):
        """Texto sem nenhum objeto JSON deve lançar ValueError."""
        service = self._criar_service_ollama("Não consegui classificar este chamado.")
        with pytest.raises(ValueError, match="JSON estruturado"):
            service.classificar_ticket("Descrição do chamado")

    # --- Erros de validação de domínio ---

    def test_categoria_invalida_erro(self):
        """Deve lançar ValidationError se a categoria estiver fora do domínio."""
        resposta = json.dumps({
            "title": "Título",
            "category": "CategoriaInexistente",
            "priority": "Alta",
        })

        service = self._criar_service_ollama(resposta)
        with pytest.raises(ValidationError, match="Categoria inválida"):
            service.classificar_ticket("Descrição do chamado")

    def test_prioridade_invalida_erro(self):
        """Deve lançar ValidationError se a prioridade estiver fora do domínio."""
        resposta = json.dumps({
            "title": "Título",
            "category": "Bug",
            "priority": "Extrema",
        })

        service = self._criar_service_ollama(resposta)
        with pytest.raises(ValidationError, match="Prioridade inválida"):
            service.classificar_ticket("Descrição do chamado")

    def test_campos_ausentes_erro(self):
        """Deve lançar ValidationError se campos obrigatórios estiverem ausentes."""
        resposta = json.dumps({
            "title": "Título",
            "category": "Bug",
        })

        service = self._criar_service_ollama(resposta)
        with pytest.raises(ValidationError, match="priority"):
            service.classificar_ticket("Descrição do chamado")

    # --- Prompt construído ---

    def test_prompt_contem_contrato(self):
        """O prompt deve conter o contrato, categorias e prioridades válidas."""
        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="ollama")), \
             patch("app.services.llm.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            service = LLMService()

            prompt = service._build_classification_prompt("Descrição de teste")

            assert '"title"' in prompt
            assert '"category"' in prompt
            assert '"priority"' in prompt
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
            assert "Descrição de teste" in prompt

    def test_prompt_enviado_ao_modelo(self):
        """O prompt construído deve ser enviado ao modelo via chat.completions."""
        descricao = "A API de pagamentos está retornando erro 500."
        resposta = json.dumps({
            "title": "API de pagamentos retornando erro 500",
            "category": "Financeiro",
            "priority": "Crítica",
        })

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=resposta))]
        )

        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="ollama")), \
             patch("app.services.llm.OpenAI", return_value=mock_client):
            service = LLMService()
            service.classificar_ticket(descricao)

            prompt_enviado = mock_client.chat.completions.create.call_args.kwargs[
                "messages"
            ][0]["content"]
            assert "contrato" in prompt_enviado.lower()
            assert descricao in prompt_enviado
            assert "Financeiro" in prompt_enviado
            assert "Crítica" in prompt_enviado


class TestExtractJson:
    """Testes do método _extract_json."""

    def setup_method(self):
        with patch("app.services.llm.settings", new=Settings(LLM_PROVIDER="ollama")), \
             patch("app.services.llm.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            self.service = LLMService()

    def test_json_puro(self):
        """JSON puro deve ser extraído diretamente."""
        data = self.service._extract_json('{"title": "T", "category": "Bug", "priority": "Alta"}')
        assert data == {"title": "T", "category": "Bug", "priority": "Alta"}

    def test_json_markdown(self):
        """JSON em bloco markdown deve ser extraído."""
        resposta = '```json\n{"title": "T", "category": "Bug", "priority": "Alta"}\n```'
        data = self.service._extract_json(resposta)
        assert data == {"title": "T", "category": "Bug", "priority": "Alta"}

    def test_json_com_texto_ao_redor(self):
        """JSON com texto ao redor deve ser extraído."""
        resposta = 'Aqui: {"title": "T", "category": "Bug", "priority": "Alta"} Fim.'
        data = self.service._extract_json(resposta)
        assert data == {"title": "T", "category": "Bug", "priority": "Alta"}

    def test_json_com_quebras_de_linha(self):
        """JSON com quebras de linha deve ser extraído."""
        resposta = '{\n  "title": "T",\n  "category": "Bug",\n  "priority": "Alta"\n}'
        data = self.service._extract_json(resposta)
        assert data == {"title": "T", "category": "Bug", "priority": "Alta"}

    def test_nao_json_erro(self):
        """Texto sem JSON deve lançar ValueError."""
        with pytest.raises(ValueError, match="JSON estruturado"):
            self.service._extract_json("Isso não é JSON")

    def test_lista_erro(self):
        """JSON que é lista deve lançar ValueError."""
        with pytest.raises(ValueError, match="JSON estruturado"):
            self.service._extract_json('["a", "b"]')