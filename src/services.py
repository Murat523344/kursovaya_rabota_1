import logging
from typing import Any, Dict, List

import pandas as pd

from .utils import find_person_transfers, find_phone_transactions, search_transactions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def serialize_transaction(t: dict) -> dict:
    """Конвертирует Timestamp в строки для JSON."""
    t_copy = t.copy()
    for key in ["Дата операции", "Дата платежа"]:
        val = t_copy.get(key)
        if pd.isna(val):
            t_copy[key] = ""
        elif isinstance(val, pd.Timestamp):
            t_copy[key] = val.strftime("%d.%m.%Y %H:%M:%S")
        else:
            t_copy[key] = str(val)
    return t_copy


def profitable_categories(data: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
    """Выгодные категории кешбэка."""
    result = {}
    for t in data:
        dt = t.get("Дата операции")
        if pd.isna(dt):
            continue
        if isinstance(dt, str):
            try:
                dt = pd.to_datetime(dt, dayfirst=True)
            except Exception:
                continue
        if dt.year == year and dt.month == month:
            cat = t.get("Категория", "Неизвестная")
            result[cat] = result.get(cat, 0) + (t.get("Сумма платежа", 0) / 100)
    logger.info("Анализ выгодных категорий завершен")
    return {k: round(v, 2) for k, v in result.items()}


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Инвесткопилка через округление."""
    total = 0
    for t in transactions:
        dt = t.get("Дата операции")
        if pd.isna(dt):
            continue
        if isinstance(dt, pd.Timestamp):
            dt_str = dt.strftime("%Y-%m")
        else:
            dt_str = str(dt)[:7]
        if dt_str != month:
            continue
        amount = t.get("Сумма операции", 0)
        remainder = limit - (amount % limit)
        total += remainder if remainder != limit else 0
    logger.info("Инвесткопилка рассчитана")
    return float(round(total, 2))


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = search_transactions(transactions, query)
    return [serialize_transaction(t) for t in results]


def phone_search(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = find_phone_transactions(transactions)
    return [serialize_transaction(t) for t in results]


def person_transfers_search(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = find_person_transfers(transactions)
    return [serialize_transaction(t) for t in results]
