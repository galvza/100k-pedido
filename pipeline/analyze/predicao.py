"""Modelo preditivo de atraso na entrega.

Classifica pedidos em "atrasado" (1) ou "no prazo" (0) usando
Logistic Regression ou Random Forest. Features extraídas via JOIN
de orders, order_items, products e customers.

Limitação conhecida (L07): sem dados de tráfego, estoque ou
sazonalidade do vendedor — performance será moderada. Apresentado
como exercício de pipeline, não solução definitiva.
"""

from __future__ import annotations

import logging
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from pipeline.config import RANDOM_STATE

logger = logging.getLogger(__name__)


def criar_features(db_path: str) -> pd.DataFrame:
    """Extrai features dos dados para modelo de atraso.

    Faz JOIN de orders + order_items + products + customers.
    Só inclui pedidos com status 'delivered' e ambas as datas
    (delivered_customer_date e estimated_delivery_date) preenchidas.

    Target: 1 se entrega real > estimativa, 0 caso contrário.

    Features criadas:
        - peso_g: peso do produto (product_weight_g)
        - frete: valor do frete (freight_value)
        - preco: preço do item (price)
        - estado_cliente: UF do cliente (customer_state)
        - distancia_estimada_dias: dias entre compra e estimativa
        - volume_cm3: volume do produto (L × A × W)

    Args:
        db_path: Caminho pro arquivo DuckDB.

    Returns:
        DataFrame com features e coluna target 'atraso'.
    """
    con = duckdb.connect(db_path, read_only=True)
    try:
        query = """
            SELECT
                o.order_id,
                o.order_delivered_customer_date,
                o.order_estimated_delivery_date,
                o.order_purchase_timestamp,
                oi.price,
                oi.freight_value,
                p.product_weight_g,
                p.product_length_cm,
                p.product_height_cm,
                p.product_width_cm,
                c.customer_state
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
              AND o.order_delivered_customer_date IS NOT NULL
              AND o.order_estimated_delivery_date IS NOT NULL
        """
        df = con.execute(query).fetchdf()
    finally:
        con.close()

    logger.info("Registros extraídos do banco: %d", len(df))

    if df.empty:
        logger.warning("Nenhum registro encontrado — DataFrame vazio")
        return df

    # Target: 1 se entregue com atraso, 0 caso contrário
    df["atraso"] = (
        df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
    ).astype(int)

    # Feature: distância estimada em dias (compra → estimativa)
    df["distancia_estimada_dias"] = (
        df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]
    ).dt.days

    # Feature: volume do produto
    df["volume_cm3"] = (
        df["product_length_cm"].fillna(0)
        * df["product_height_cm"].fillna(0)
        * df["product_width_cm"].fillna(0)
    )

    # Renomear pra nomes limpos
    df = df.rename(
        columns={
            "product_weight_g": "peso_g",
            "freight_value": "frete",
            "price": "preco",
            "customer_state": "estado_cliente",
        }
    )

    # Selecionar colunas finais
    colunas_finais = [
        "order_id",
        "peso_g",
        "frete",
        "preco",
        "estado_cliente",
        "distancia_estimada_dias",
        "volume_cm3",
        "atraso",
    ]
    df = df[colunas_finais]

    n_atrasados = df["atraso"].sum()
    logger.info(
        "Target: %d atrasados (%.1f%%) de %d pedidos",
        n_atrasados,
        100 * n_atrasados / len(df),
        len(df),
    )

    return df


def preparar_dados(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = RANDOM_STATE,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Remove NaN, codifica categorias e faz split estratificado.

    Args:
        df: DataFrame com features e coluna 'atraso'.
        test_size: Proporção do conjunto de teste.
        random_state: Seed pra reprodutibilidade.

    Returns:
        Tupla (X_train, X_test, y_train, y_test, feature_names).
    """
    # Remover order_id (não é feature)
    df_work = df.drop(columns=["order_id"], errors="ignore").copy()

    n_antes = len(df_work)
    df_work = df_work.dropna()
    n_removido = n_antes - len(df_work)
    if n_removido > 0:
        logger.warning(
            "Removidas %d linhas com NaN (de %d para %d)",
            n_removido,
            n_antes,
            len(df_work),
        )

    # Encode estado_cliente com LabelEncoder
    le = LabelEncoder()
    df_work["estado_cliente"] = le.fit_transform(df_work["estado_cliente"].astype(str))

    # Separar features e target
    feature_cols = [c for c in df_work.columns if c != "atraso"]
    X = df_work[feature_cols].values
    y = df_work["atraso"].values

    # Split estratificado
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    logger.info(
        "Split: treino=%d, teste=%d (%.0f%%/%.0f%%)",
        len(X_train),
        len(X_test),
        100 * len(X_train) / len(X),
        100 * len(X_test) / len(X),
    )

    return X_train, X_test, y_train, y_test, feature_cols


def treinar_modelo(
    X_train: np.ndarray,
    y_train: np.ndarray,
    modelo: str = "logistic",
    random_state: int = RANDOM_STATE,
) -> Any:
    """Treina modelo de classificação binária.

    Args:
        X_train: Features de treino.
        y_train: Target de treino.
        modelo: 'logistic' para LogisticRegression,
                'random_forest' para RandomForestClassifier.
        random_state: Seed pra reprodutibilidade.

    Returns:
        Modelo treinado (sklearn estimator).

    Raises:
        ValueError: Se modelo não é 'logistic' nem 'random_forest'.
    """
    if modelo == "logistic":
        clf = LogisticRegression(
            class_weight="balanced",
            random_state=random_state,
            max_iter=1000,
            solver="lbfgs",
        )
    elif modelo == "random_forest":
        clf = RandomForestClassifier(
            class_weight="balanced",
            random_state=random_state,
            n_estimators=100,
            n_jobs=-1,
        )
    else:
        raise ValueError(
            f"Modelo '{modelo}' não suportado. Use 'logistic' ou 'random_forest'."
        )

    clf.fit(X_train, y_train)
    logger.info("Modelo '%s' treinado com %d amostras", modelo, len(X_train))
    return clf


def avaliar_modelo(
    modelo: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> dict:
    """Avalia modelo com métricas de classificação.

    Args:
        modelo: Modelo sklearn treinado.
        X_test: Features de teste.
        y_test: Target de teste.

    Returns:
        Dict com accuracy, precision, recall, f1, auc_roc,
        confusion_matrix e classification_report.
    """
    y_pred = modelo.predict(X_test)

    # AUC-ROC precisa de probabilidades
    if hasattr(modelo, "predict_proba"):
        y_proba = modelo.predict_proba(X_test)[:, 1]
        auc = round(float(roc_auc_score(y_test, y_proba)), 4)
    else:
        auc = None

    acc = round(float(accuracy_score(y_test, y_pred)), 4)
    prec = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
    rec = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
    f1 = round(float(f1_score(y_test, y_pred, zero_division=0)), 4)
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, zero_division=0)

    if acc < 0.5:
        logger.warning("Modelo não supera baseline: accuracy=%.4f < 0.5", acc)

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "auc_roc": auc,
        "confusion_matrix": cm,
        "classification_report": report,
    }


def pipeline_predicao(db_path: str) -> dict:
    """Pipeline completo de predição de atraso.

    Orquestra: extração de features → preparação → treino
    (logistic + random_forest) → avaliação → feature importances.

    Args:
        db_path: Caminho pro arquivo DuckDB.

    Returns:
        Dict com: metricas_logistic, metricas_rf, feature_importances,
        feature_names, n_original, n_usado, proporcao_atraso.
    """
    # Extrair features
    df = criar_features(db_path)

    n_original = len(df)

    if n_original < 10:
        logger.error("Dados insuficientes para modelagem: %d registros", n_original)
        return {
            "metricas_logistic": None,
            "metricas_rf": None,
            "feature_importances": None,
            "feature_names": None,
            "n_original": n_original,
            "n_usado": 0,
            "proporcao_atraso": None,
        }

    # Preparar dados
    X_train, X_test, y_train, y_test, feature_names = preparar_dados(df)

    n_usado = len(X_train) + len(X_test)
    proporcao_atraso = round(float(df["atraso"].mean()), 4)

    # Treinar e avaliar Logistic Regression
    modelo_lr = treinar_modelo(X_train, y_train, modelo="logistic")
    metricas_lr = avaliar_modelo(modelo_lr, X_test, y_test)

    # Treinar e avaliar Random Forest
    modelo_rf = treinar_modelo(X_train, y_train, modelo="random_forest")
    metricas_rf = avaliar_modelo(modelo_rf, X_test, y_test)

    # Feature importances do Random Forest
    importances = modelo_rf.feature_importances_
    feature_importances = [
        {"feature": name, "importance": round(float(imp), 4)}
        for name, imp in sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True,
        )
    ]

    logger.info(
        "Pipeline concluído. LR accuracy=%.4f, RF accuracy=%.4f",
        metricas_lr["accuracy"],
        metricas_rf["accuracy"],
    )

    return {
        "metricas_logistic": metricas_lr,
        "metricas_rf": metricas_rf,
        "feature_importances": feature_importances,
        "feature_names": feature_names,
        "n_original": n_original,
        "n_usado": n_usado,
        "proporcao_atraso": proporcao_atraso,
    }
