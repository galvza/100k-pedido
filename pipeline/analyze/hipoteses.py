"""Testes de hipótese estatísticos.

Funções para validar hipóteses de negócio com testes
não-paramétricos (Mann-Whitney U) e paramétricos (t-test).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from pipeline.config import SIGNIFICANCE_LEVEL


def mann_whitney_test(
    grupo_a: pd.Series,
    grupo_b: pd.Series,
    alpha: float = SIGNIFICANCE_LEVEL,
) -> dict:
    """Teste Mann-Whitney U para duas amostras independentes.

    Teste não-paramétrico: não assume normalidade.
    Ideal para comparar distribuições de review scores,
    tempos de entrega, etc.

    Args:
        grupo_a: Primeira amostra.
        grupo_b: Segunda amostra.
        alpha: Nível de significância.

    Returns:
        Dict com u_statistic, p_value, significativo, tamanho_efeito,
        n_a, n_b e teste_usado.
    """
    a = grupo_a.dropna()
    b = grupo_b.dropna()

    if len(a) < 2 or len(b) < 2:
        return {
            "teste_usado": "Mann-Whitney U",
            "u_statistic": None,
            "p_value": None,
            "significativo": None,
            "tamanho_efeito": None,
            "n_a": len(a),
            "n_b": len(b),
            "alpha": alpha,
            "mensagem": "Amostra insuficiente",
        }

    u_stat, p_value = stats.mannwhitneyu(a, b, alternative="two-sided")

    # Tamanho de efeito: rank-biserial correlation r = 1 - (2U)/(n1*n2)
    n_a, n_b = len(a), len(b)
    r = 1.0 - (2.0 * u_stat) / (n_a * n_b)

    return {
        "teste_usado": "Mann-Whitney U",
        "u_statistic": round(float(u_stat), 4),
        "p_value": round(float(p_value), 6),
        "significativo": bool(p_value < alpha),
        "tamanho_efeito": round(float(r), 4),
        "n_a": n_a,
        "n_b": n_b,
        "alpha": alpha,
        "mensagem": None,
    }


def t_test_independente(
    grupo_a: pd.Series,
    grupo_b: pd.Series,
    alpha: float = SIGNIFICANCE_LEVEL,
) -> dict:
    """Teste t de Student para duas amostras independentes.

    Usa Welch's t-test (equal_var=False) por padrão, que não
    assume variâncias iguais — mais robusto.

    Args:
        grupo_a: Primeira amostra.
        grupo_b: Segunda amostra.
        alpha: Nível de significância.

    Returns:
        Dict com t_statistic, p_value, significativo, cohens_d,
        n_a, n_b e teste_usado.
    """
    a = grupo_a.dropna()
    b = grupo_b.dropna()

    if len(a) < 2 or len(b) < 2:
        return {
            "teste_usado": "Welch t-test",
            "t_statistic": None,
            "p_value": None,
            "significativo": None,
            "cohens_d": None,
            "n_a": len(a),
            "n_b": len(b),
            "alpha": alpha,
            "mensagem": "Amostra insuficiente",
        }

    t_stat, p_value = stats.ttest_ind(a, b, equal_var=False)

    # Cohen's d: diferença de médias normalizada pelo desvio padrão pooled
    mean_diff = float(a.mean() - b.mean())
    n_a, n_b = len(a), len(b)
    var_a, var_b = float(a.var(ddof=1)), float(b.var(ddof=1))
    pooled_std = math.sqrt(
        ((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)
    )
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0

    return {
        "teste_usado": "Welch t-test",
        "t_statistic": round(float(t_stat), 4),
        "p_value": round(float(p_value), 6),
        "significativo": bool(p_value < alpha),
        "cohens_d": round(float(cohens_d), 4),
        "n_a": n_a,
        "n_b": n_b,
        "alpha": alpha,
        "mensagem": None,
    }


def resultado_formatado(teste: dict, hipotese: str) -> dict:
    """Adiciona descrição textual ao resultado do teste.

    Args:
        teste: Dict retornado por mann_whitney_test ou t_test_independente.
        hipotese: Descrição da hipótese testada.

    Returns:
        Dict original enriquecido com hipotese, conclusao e premissas.
    """
    resultado = {**teste, "hipotese": hipotese}

    if teste.get("mensagem") == "Amostra insuficiente":
        resultado["conclusao"] = (
            f"Inconclusivo: amostra insuficiente "
            f"(n_a={teste['n_a']}, n_b={teste['n_b']}). "
            f"Minimo de 2 observacoes por grupo."
        )
        resultado["premissas"] = "Teste nao executado."
        return resultado

    teste_nome = teste["teste_usado"]
    p = teste["p_value"]
    alpha = teste["alpha"]
    n_total = teste["n_a"] + teste["n_b"]

    if teste["significativo"]:
        conclusao = (
            f"Rejeita H0 (p={p:.4f} < alpha={alpha}). "
            f"Ha diferenca estatisticamente significativa."
        )
    else:
        conclusao = (
            f"Nao rejeita H0 (p={p:.4f} >= alpha={alpha}). "
            f"Nao ha evidencia de diferenca significativa."
        )

    # Tamanho de efeito
    if "cohens_d" in teste and teste["cohens_d"] is not None:
        d = abs(teste["cohens_d"])
        if d < 0.2:
            efeito = "negligivel"
        elif d < 0.5:
            efeito = "pequeno"
        elif d < 0.8:
            efeito = "medio"
        else:
            efeito = "grande"
        conclusao += f" Tamanho do efeito (Cohen's d): {teste['cohens_d']:.4f} ({efeito})."
    elif "tamanho_efeito" in teste and teste["tamanho_efeito"] is not None:
        r = abs(teste["tamanho_efeito"])
        if r < 0.1:
            efeito = "negligivel"
        elif r < 0.3:
            efeito = "pequeno"
        elif r < 0.5:
            efeito = "medio"
        else:
            efeito = "grande"
        conclusao += f" Tamanho do efeito (r): {teste['tamanho_efeito']:.4f} ({efeito})."

    resultado["conclusao"] = conclusao

    if teste_nome == "Mann-Whitney U":
        resultado["premissas"] = (
            f"Teste nao-parametrico (nao assume normalidade). "
            f"Amostras independentes. n={n_total} "
            f"(n_a={teste['n_a']}, n_b={teste['n_b']}). "
            f"Nivel de significancia: {alpha}."
        )
    else:
        resultado["premissas"] = (
            f"Welch t-test (nao assume variancias iguais). "
            f"Amostras independentes. n={n_total} "
            f"(n_a={teste['n_a']}, n_b={teste['n_b']}). "
            f"Nivel de significancia: {alpha}."
        )

    return resultado
