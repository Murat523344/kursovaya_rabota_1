import json
import logging
from functools import wraps
from typing import Any, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def save_report(filename: Optional[str] = None):
    """Декоратор для записи отчёта в файл"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            fname = filename or f"report_{func.__name__}.json"
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                logger.info("Отчёт сохранён в %s", fname)
            except Exception as e:
                logger.error("Ошибка сохранения отчёта: %s", e)
            return result
        return wrapper
    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Траты по категории за последние 3 месяца"""
    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
    if date:
        dt = pd.to_datetime(date)
    else:
        dt = pd.Timestamp.now()
    start = dt - pd.DateOffset(months=3)
    df = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= dt)]
    df_cat = df[df["Категория"] == category]
    total = round(df_cat["Сумма платежа"].sum())
    return {"category": category, "total_amount": total}


@save_report()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> Dict[str, Any]:
    """Средние траты по дням недели за последние 3 месяца"""
    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
    if date:
        dt = pd.to_datetime(date)
    else:
        dt = pd.Timestamp.now()
    start = dt - pd.DateOffset(months=3)
    df = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= dt)]
    df["weekday"] = df["Дата операции"].dt.day_name()
    result = df.groupby("weekday")["Сумма платежа"].mean().round(2).to_dict()
    return result


@save_report()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> Dict[str, Any]:
    """Средние траты в рабочие и выходные дни за последние 3 месяца"""
    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
    if date:
        dt = pd.to_datetime(date)
    else:
        dt = pd.Timestamp.now()
    start = dt - pd.DateOffset(months=3)
    df = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= dt)]
    df["is_workday"] = df["Дата операции"].dt.weekday < 5
    result = df.groupby("is_workday")["Сумма платежа"].mean().round(2).to_dict()
    return {"workday": result.get(True, 0), "weekend": result.get(False, 0)}
