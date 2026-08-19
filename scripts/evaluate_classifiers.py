"""
Script de experimento: compara o classificador heurístico com o LLMClassifier.

Lê o dataset de avaliação (tests/evaluation/ticket_dataset.json),
executa cada caso contra ambos os classificadores e imprime:
- resultado por caso;
- acertos de categoria e prioridade;
- percentuais de acerto;
- tempo de execução.

Uso:
    python scripts/evaluate_classifiers.py
"""

import json
import sys
import time
from pathlib import Path

# Garante saída UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Adiciona a raiz do projeto ao path para importar `app`
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services import LLMClassifier, TicketClassifier

DATASET_PATH = PROJECT_ROOT / "tests" / "evaluation" / "ticket_dataset.json"


def carregar_dataset(path: Path) -> list[dict]:
    """Carrega o dataset de avaliação."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def avaliar_classificador(classificador, dataset: list[dict], nome: str) -> None:
    """
    Executa o classificador contra o dataset e imprime os resultados.

    Args:
        classificador: Objeto com método `classify(description)`.
        dataset: Lista de casos com description, expected_category, expected_priority.
        nome: Nome do classificador para exibição.
    """
    total = len(dataset)
    acertos_categoria = 0
    acertos_prioridade = 0
    tempos: list[float] = []

    print(f"\n{'=' * 60}")
    print(f"  {nome}")
    print(f"{'=' * 60}")

    for caso in dataset:
        descricao = caso["description"]
        expected_cat = caso["expected_category"]
        expected_pri = caso["expected_priority"]

        inicio = time.perf_counter()
        try:
            resultado = classificador.classify(descricao)
            # Heurístico retorna dict; LLM retorna Pydantic model
            if isinstance(resultado, dict):
                cat = resultado.get("category")
                pri = resultado.get("priority")
            else:
                cat = resultado.category
                pri = resultado.priority
        except Exception as exc:  # noqa: BLE001 - experimento deve continuar
            cat = f"ERRO: {exc}"
            pri = f"ERRO: {exc}"
        fim = time.perf_counter()
        tempo = fim - inicio
        tempos.append(tempo)

        if cat == expected_cat:
            acertos_categoria += 1
        if pri == expected_pri:
            acertos_prioridade += 1

        print(f"\nDescription: {descricao!r}")
        print(f"  Expected:  category={expected_cat}  priority={expected_pri}")
        print(f"  {nome}: category={cat}  priority={pri}")
        print(f"  Tempo: {tempo:.2f}s")

    # Métricas
    pct_cat = (acertos_categoria / total) * 100
    pct_pri = (acertos_prioridade / total) * 100
    tempo_total = sum(tempos)
    tempo_medio = tempo_total / total if total else 0

    print(f"\n{'-' * 60}")
    print(f"  Resumo ({nome})")
    print(f"  Total de casos: {total}")
    print(f"  Acertos de categoria: {acertos_categoria}/{total} ({pct_cat:.0f}%)")
    print(f"  Acertos de prioridade: {acertos_prioridade}/{total} ({pct_pri:.0f}%)")
    print(f"  Tempo total: {tempo_total:.2f}s")
    print(f"  Tempo médio por ticket: {tempo_medio:.2f}s")


def main() -> None:
    """Executa o experimento de comparação."""
    dataset = carregar_dataset(DATASET_PATH)
    print(f"Dataset carregado: {len(dataset)} casos de {DATASET_PATH}")

    heuristico = TicketClassifier()
    llm = LLMClassifier()

    avaliar_classificador(heuristico, dataset, "Heuristic")
    avaliar_classificador(llm, dataset, "LLM")


if __name__ == "__main__":
    main()