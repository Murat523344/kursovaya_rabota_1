import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from .utils import get_currency_rates, get_stock_prices

logger = logging.getLogger(__name__)


def greeting_by_time(dt: datetime) -> str:
    """Приветствие по времени суток."""
    hour = dt.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    if 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def get_card_last_digits(card_value) -> str:
    """Последние 4 цифры карты."""
    if pd.isna(card_value):
        return "0000"
    try:
        return str(int(card_value))[-4:]
    except Exception:
        return "0000"


def main_page(date_str: str, transactions: List[Dict[str, Any]], user_settings: Dict[str, Any]) -> Dict[str, Any]:
    """JSON для страницы 'Главная'."""
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    greeting = greeting_by_time(dt)

    cards = {}
    for t in transactions:
        card = get_card_last_digits(t.get("Номер карты"))
        cards.setdefault(card, 0)
        cards[card] += t.get("Сумма платежа", 0)

    cards_list = [
        {
            "last_digits": k,
            "total_spent": round(v, 2),
            "cashback": round(v / 100, 2)
        }
        for k, v in cards.items()
    ]

    top_transactions = sorted(transactions, key=lambda x: x.get("Сумма платежа", 0), reverse=True)[:5]
    top_list = []
    for t in top_transactions:
        date_val = t.get("Дата операции")
        if pd.isna(date_val):
            date_str = ""
        elif isinstance(date_val, pd.Timestamp):
            date_str = date_val.strftime("%d.%m.%Y")
        else:
            date_str = str(date_val)
        top_list.append({
            "date": date_str,
            "amount": round(t.get("Сумма платежа", 0), 2),
            "category": t.get("Категория", ""),
            "description": t.get("Описание", "")
        })

    currency_rates = get_currency_rates(user_settings.get("user_currencies", []))
    stock_prices = get_stock_prices(user_settings.get("user_stocks", []))

    return {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_list,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
