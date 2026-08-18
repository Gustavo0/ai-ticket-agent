"""
Testes dos serviços de estruturação e classificação de chamados.
"""

from app.services import TicketClassifier, TicketStructuringService


class TestTicketStructuringService:
    """Testes do serviço de estruturação de chamados."""

    def setup_method(self):
        self.service = TicketStructuringService()

    def test_structure_returns_dict(self):
        """structure deve retornar um dicionário."""
        result = self.service.structure("A API de pagamentos está retornando erro 500.")
        assert isinstance(result, dict)

    def test_structure_returns_expected_keys(self):
        """structure deve retornar as chaves title, category e priority."""
        result = self.service.structure("A API de pagamentos está retornando erro 500.")
        assert set(result.keys()) == {"title", "category", "priority"}

    def test_generate_title_short_description(self):
        """Título de descrição curta deve ser a própria descrição."""
        description = "Descrição curta."
        assert self.service._generate_title(description) == description

    def test_generate_title_long_description(self):
        """Título de descrição longa deve ser truncado em 10 palavras."""
        description = "Esta é uma descrição muito longa que deve ser truncada em exatamente dez palavras ou mais"
        title = self.service._generate_title(description)
        assert len(title.split()) == 10
        assert title.endswith("...")

    def test_infer_category_financeiro(self):
        """Deve inferir categoria Financeiro para texto de pagamento."""
        result = self.service.structure("A API de pagamentos está retornando erro 500.")
        assert result["category"] == "Financeiro"

    def test_infer_category_bug(self):
        """Deve inferir categoria Bug para texto de erro/exception."""
        result = self.service.structure("Estou recebendo uma exception ao salvar os dados.")
        assert result["category"] == "Bug"

    def test_infer_category_suporte(self):
        """Deve inferir categoria Suporte para texto de acesso/senha."""
        result = self.service.structure("Não consigo acessar o sistema com minha senha.")
        assert result["category"] == "Suporte"

    def test_infer_category_melhoria(self):
        """Deve inferir categoria Melhoria para texto de sugestão."""
        result = self.service.structure("Seria bom ter um relatório de chamados resolvidos por mês.")
        assert result["category"] == "Melhoria"

    def test_infer_category_infraestrutura(self):
        """Deve inferir categoria Infraestrutura para texto de servidor."""
        result = self.service.structure("O servidor de banco de dados está fora do ar.")
        assert result["category"] == "Infraestrutura"

    def test_infer_priority_critica(self):
        """Deve inferir prioridade Crítica para texto urgente."""
        result = self.service.structure("O sistema está fora do ar e todos os usuários foram afetados!")
        assert result["priority"] == "Crítica"

    def test_infer_priority_alta(self):
        """Deve inferir prioridade Alta para texto de bloqueio."""
        result = self.service.structure("O processo está bloqueado e não consigo continuar.")
        assert result["priority"] == "Alta"

    def test_infer_priority_media(self):
        """Deve inferir prioridade Média para texto de lentidão intermitente."""
        result = self.service.structure("O sistema está com lentidão intermitente para alguns usuários.")
        assert result["priority"] == "Média"

    def test_infer_priority_baixa(self):
        """Deve inferir prioridade Baixa para texto de melhoria cosmética."""
        result = self.service.structure("Seria uma melhoria cosmética no layout, quando puder.")
        assert result["priority"] == "Baixa"

    def test_structure_no_keywords_returns_none_category(self):
        """Sem palavras-chave, a categoria deve ser None."""
        result = self.service.structure("Texto sem palavras-chave relevantes aqui.")
        assert result["category"] is None

    def test_structure_no_keywords_returns_none_priority(self):
        """Sem palavras-chave, a prioridade deve ser None."""
        result = self.service.structure("Texto sem palavras-chave relevantes aqui.")
        assert result["priority"] is None


class TestTicketClassifier:
    """Testes do classificador de chamados."""

    def setup_method(self):
        self.classifier = TicketClassifier()

    def test_classify_returns_dict(self):
        """classify deve retornar um dicionário."""
        result = self.classifier.classify("A API de pagamentos está retornando erro 500.")
        assert isinstance(result, dict)

    def test_classify_returns_expected_keys(self):
        """classify deve retornar chaves title, category e priority."""
        result = self.classifier.classify("A API de pagamentos está retornando erro 500.")
        assert set(result.keys()) == {"title", "category", "priority"}

    def test_classify_infers_category(self):
        """classify deve inferir a categoria."""
        result = self.classifier.classify("A API de pagamentos está retornando erro 500.")
        assert result["category"] == "Financeiro"

    def test_classify_infers_priority(self):
        """classify deve inferir a prioridade."""
        result = self.classifier.classify("O sistema está fora do ar.")
        assert result["priority"] == "Crítica"

    def test_generate_title(self):
        """generate_title deve gerar um título a partir da descrição."""
        title = self.classifier.generate_title("Descrição curta.")
        assert title == "Descrição curta."