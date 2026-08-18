"""
Teste de integração com a LLM (Ollama / OpenAI).

Executa uma chamada simples ao modelo ativo do provedor configurado
no arquivo .env (`LLM_PROVIDER`).

Uso:
    python test_llm.py
"""

from openai import APIConnectionError, AuthenticationError, OpenAIError, RateLimitError

from app.services.llm import llm_service

print(f"Provedor ativo: {llm_service.provider_ativo}")
print(f"Modelo ativo:   {llm_service.modelo_ativo}")
print(f"Solicitando resposta...\n")

try:
    resposta = llm_service.responder(
        "Explique em uma frase o que é um erro HTTP 500."
    )
    print(resposta)

except APIConnectionError as exc:
    print(
        "ERRO DE CONEXÃO: não foi possível conectar ao provedor de LLM.\n"
        "\n"
        "Se estiver usando o Ollama (padrão):\n"
        "  1. Instale o Ollama em https://ollama.com/download\n"
        "  2. Inicie o servidor:\n"
        "       ollama serve\n"
        "  3. Baixe o modelo configurado:\n"
        f"       ollama pull {llm_service.modelo_ativo}\n"
        "\n"
        "Se estiver usando a OpenAI, verifique sua conexão com a internet."
    )
    print(f"\nDetalhes: {exc}")

except AuthenticationError as exc:
    print("ERRO DE AUTENTICAÇÃO: chave da API inválida ou ausente.")
    print(f"Detalhes: {exc}")

except RateLimitError as exc:
    print("ERRO DE COTA/LIMITE: a conta excedeu a cota ou saldo disponível.")
    print("Acesse https://platform.openai.com/settings/billing para verificar o plano.")
    print(f"Detalhes: {exc}")

except OpenAIError as exc:
    print(f"ERRO NA API DO PROVEDOR: {exc}")