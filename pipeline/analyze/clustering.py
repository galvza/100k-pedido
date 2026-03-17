"""Segmentação automática de clientes via K-Means sobre features RFM.

Normaliza R, F, M com StandardScaler, avalia k ótimo via Elbow
e Silhouette, roda K-Means final.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from pipeline.config import RANDOM_STATE

logger = logging.getLogger(__name__)


def normalizar_features(
    df: pd.DataFrame,
    colunas: list[str],
) -> tuple[np.ndarray, StandardScaler]:
    """Normaliza colunas com StandardScaler (mean=0, std=1).

    Args:
        df: DataFrame com as features.
        colunas: Lista de colunas pra normalizar.

    Returns:
        Tupla (X_scaled, scaler).
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(df[colunas].values)
    return X, scaler


def elbow_method(
    X: np.ndarray,
    k_range: range = range(2, 11),
    random_state: int = RANDOM_STATE,
) -> list[dict]:
    """Calcula inércia (WCSS) pra cada k — usado no gráfico Elbow.

    Args:
        X: Features normalizadas (n_samples, n_features).
        k_range: Range de valores de k pra testar.
        random_state: Seed pra reprodutibilidade.

    Returns:
        Lista de dicts [{k, inertia}].
    """
    results = []
    max_k = min(max(k_range), X.shape[0])
    for k in k_range:
        if k > max_k:
            break
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        km.fit(X)
        results.append({"k": k, "inertia": round(float(km.inertia_), 4)})
    return results


def silhouette_scores(
    X: np.ndarray,
    k_range: range = range(2, 11),
    random_state: int = RANDOM_STATE,
) -> list[dict]:
    """Calcula Silhouette score pra cada k.

    Args:
        X: Features normalizadas.
        k_range: Range de valores de k.
        random_state: Seed.

    Returns:
        Lista de dicts [{k, silhouette}].
    """
    results = []
    max_k = min(max(k_range), X.shape[0] - 1)
    for k in k_range:
        if k > max_k:
            break
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(X)
        score = silhouette_score(X, labels)
        results.append({"k": k, "silhouette": round(float(score), 4)})
    return results


def rodar_kmeans(
    X: np.ndarray,
    k: int,
    random_state: int = RANDOM_STATE,
) -> dict:
    """Roda K-Means com k clusters.

    Args:
        X: Features normalizadas.
        k: Número de clusters.
        random_state: Seed.

    Returns:
        Dict com labels, centroids, inertia, k.
    """
    km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = km.fit_predict(X)
    return {
        "k": k,
        "labels": labels,
        "centroids": km.cluster_centers_,
        "inertia": round(float(km.inertia_), 4),
    }


def pipeline_clustering(
    df_rfm: pd.DataFrame,
    colunas: list[str] | None = None,
    k_range: range = range(2, 11),
) -> dict:
    """Pipeline completo de clustering RFM.

    Orquestra: limpeza → normalização → elbow → silhouette → K-Means final.

    Args:
        df_rfm: DataFrame com colunas RFM (recency, frequency, monetary).
        colunas: Colunas pra clustering. Default: ["recency", "frequency", "monetary"].
        k_range: Range de k pra avaliar.

    Returns:
        Dict com: df_resultado, elbow, silhouette, kmeans, k_otimo,
        scaler, n_original, n_usado.
    """
    if colunas is None:
        colunas = ["recency", "frequency", "monetary"]

    n_original = len(df_rfm)

    # Remover linhas com NaN nas colunas de interesse
    df_clean = df_rfm.dropna(subset=colunas).copy()
    n_removido = n_original - len(df_clean)
    if n_removido > 0:
        logger.warning(
            "Removidas %d linhas com NaN (de %d para %d)",
            n_removido,
            n_original,
            len(df_clean),
        )

    n_usado = len(df_clean)

    if n_usado < 2:
        logger.error("Dados insuficientes para clustering: %d linhas", n_usado)
        return {
            "df_resultado": df_clean,
            "elbow": [],
            "silhouette": [],
            "kmeans": None,
            "k_otimo": None,
            "scaler": None,
            "n_original": n_original,
            "n_usado": n_usado,
        }

    # Ajustar k_range se necessário
    max_k = n_usado - 1
    effective_range = range(k_range.start, min(k_range.stop, max_k + 1))

    # Normalizar
    X, scaler = normalizar_features(df_clean, colunas)

    # Elbow e Silhouette
    elbow_results = elbow_method(X, k_range=effective_range)
    silhouette_results = silhouette_scores(X, k_range=effective_range)

    # k ótimo = maior silhouette score
    k_otimo = max(silhouette_results, key=lambda x: x["silhouette"])["k"]
    logger.info("k otimo (melhor silhouette): %d", k_otimo)

    # K-Means final
    kmeans_result = rodar_kmeans(X, k_otimo)

    # Adicionar labels ao DataFrame
    df_clean["cluster"] = kmeans_result["labels"]

    return {
        "df_resultado": df_clean,
        "elbow": elbow_results,
        "silhouette": silhouette_results,
        "kmeans": kmeans_result,
        "k_otimo": k_otimo,
        "scaler": scaler,
        "n_original": n_original,
        "n_usado": n_usado,
    }
