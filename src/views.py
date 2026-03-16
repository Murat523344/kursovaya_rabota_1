import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


def _convert_to_dataframe(transactions: Union[List[Dict[str, Any]], pd.DataFrame]) -> pd.DataFrame:
    """
    Конвертирует список словарей в DataFrame.
    """
    if isinstance(transactions, list):
        return pd.DataFrame(transactions)
    return transactions


def main_page(
    date_str: str, transactions: Union[List[Dict[str, Any]], pd.DataFrame], user_settings: Dict[str, Any]
) -> str:
    """
    Генерирует JSON для главной страницы.
    """
    try:
        transactions_df = _convert_to_dataframe(transactions)
        current_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        # Определяем приветствие
        hour = current_date.hour
        if 5 <= hour < 12:
            greeting = "Доброе утро"
        elif 12 <= hour < 18:
            greeting = "Добрый день"
        elif 18 <= hour < 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        # Фильтруем за текущий месяц
        start_of_month = current_date.replace(day=1).strftime("%Y-%m-%d")
        end_date = current_date.strftime("%Y-%m-%d")

        if "Дата операции" in transactions_df.columns:
            transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], dayfirst=True)
            mask = (transactions_df["Дата операции"] >= start_of_month) & (
                transactions_df["Дата операции"] <= end_date
            )
            month_transactions = transactions_df[mask].copy()
        else:
            month_transactions = pd.DataFrame()

        # Информация по картам
        cards: List[Dict[str, Any]] = []
        if not month_transactions.empty and "Номер карты" in month_transactions.columns:
            card_numbers = month_transactions["Номер карты"].dropna().unique()

            for card_num in card_numbers:
                card_trans = month_transactions[month_transactions["Номер карты"] == card_num]
                expenses = card_trans[card_trans["Сумма платежа"] < 0]["Сумма платежа"].sum()
                card_str = str(card_num)
                digits = re.findall(r"\d", card_str)

                if digits:
                    last_digits = "".join(digits[-4:])
                else:
                    last_digits = "0000"

                cards.append(
                    {
                        "last_digits": last_digits,
                        "total_spent": abs(round(float(expenses), 2)) if expenses != 0 else 0,
                        "cashback": round(abs(float(expenses)) * 0.01, 2) if expenses != 0 else 0,
                    }
                )

        # Топ-5 транзакций
        top_transactions: List[Dict[str, Any]] = []
        if not month_transactions.empty and "Сумма платежа" in month_transactions.columns:
            month_transactions = month_transactions.copy()
            month_transactions["abs_amount"] = abs(month_transactions["Сумма платежа"])
            top5 = month_transactions.nlargest(5, "abs_amount")

            for _, trans in top5.iterrows():
                top_transactions.append(
                    {
                        "date": (
                            trans["Дата операции"].strftime("%d.%m.%Y") if pd.notna(trans["Дата операции"]) else ""
                        ),
                        "amount": round(float(trans["Сумма платежа"]), 2),
                        "category": str(trans.get("Категория", "")) if pd.notna(trans.get("Категория", "")) else "",
                        "description": str(trans.get("Описание", "")) if pd.notna(trans.get("Описание", "")) else "",
                    }
                )

        # Курсы валют
        currency_rates: List[Dict[str, Any]] = []
        for currency in user_settings.get("user_currencies", []):
            rate = 73.21 if currency == "USD" else 87.08 if currency == "EUR" else 1.0
            currency_rates.append({"currency": currency, "rate": rate})

        # Цены акций
        stock_prices: List[Dict[str, Any]] = []
        stocks = user_settings.get("user_stocks", [])
        stock_defaults = {"AAPL": 150.12, "AMZN": 3173.18, "GOOGL": 2742.39, "MSFT": 296.71, "TSLA": 1007.08}

        for stock in stocks:
            stock_prices.append({"stock": stock, "price": stock_defaults.get(stock, 100.00)})

        result = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка в main_page: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def events_page(
    date_str: str,
    transactions: Union[List[Dict[str, Any]], pd.DataFrame],
    range_option: str = "M",
    user_settings: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Генерирует JSON для страницы событий.
    """
    if user_settings is None:
        user_settings = {"user_currencies": ["USD"], "user_stocks": []}

    try:
        transactions_df = _convert_to_dataframe(transactions)

        if transactions_df.empty:
            empty_result = {
                "expenses": {"total_amount": 0, "main": [], "transfers_and_cash": []},
                "income": {"total_amount": 0, "main": []},
                "currency_rates": _get_currency_rates(user_settings),
                "stock_prices": _get_stock_prices(user_settings),
            }
            return json.dumps(empty_result, ensure_ascii=False, indent=2)

        current_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        # Определяем начальную дату
        if range_option == "W":
            start_date = (current_date - timedelta(days=current_date.weekday())).strftime("%Y-%m-%d")
        elif range_option == "M":
            start_date = current_date.replace(day=1).strftime("%Y-%m-%d")
        elif range_option == "Y":
            start_date = current_date.replace(month=1, day=1).strftime("%Y-%m-%d")
        elif range_option == "ALL":
            start_date = "2000-01-01"
        else:
            start_date = current_date.replace(day=1).strftime("%Y-%m-%d")

        end_date = current_date.strftime("%Y-%m-%d")

        if "Дата операции" in transactions_df.columns:
            transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], dayfirst=True)
            mask = (transactions_df["Дата операции"] >= start_date) & (transactions_df["Дата операции"] <= end_date)
            filtered_df = transactions_df[mask].copy()
        else:
            filtered_df = pd.DataFrame()

        if filtered_df.empty:
            result = {
                "expenses": {"total_amount": 0, "main": [], "transfers_and_cash": []},
                "income": {"total_amount": 0, "main": []},
                "currency_rates": _get_currency_rates(user_settings),
                "stock_prices": _get_stock_prices(user_settings),
            }
            return json.dumps(result, ensure_ascii=False, indent=2)

        expenses_df = filtered_df[filtered_df["Сумма платежа"] < 0].copy()
        income_df = filtered_df[filtered_df["Сумма платежа"] > 0].copy()

        result = {
            "expenses": {
                "total_amount": int(abs(expenses_df["Сумма платежа"].sum())) if not expenses_df.empty else 0,
                "main": [],
                "transfers_and_cash": [],
            },
            "income": {
                "total_amount": int(income_df["Сумма платежа"].sum()) if not income_df.empty else 0,
                "main": [],
            },
            "currency_rates": _get_currency_rates(user_settings),
            "stock_prices": _get_stock_prices(user_settings),
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка в events_page: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _get_currency_rates(user_settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Получает курсы валют (заглушка)."""
    currency_rates: List[Dict[str, Any]] = []
    for currency in user_settings.get("user_currencies", []):
        rate = 73.21 if currency == "USD" else 87.08 if currency == "EUR" else 1.0
        currency_rates.append({"currency": currency, "rate": rate})
    return currency_rates


def _get_stock_prices(user_settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Получает цены акций (заглушка)."""
    stock_prices: List[Dict[str, Any]] = []
    stocks = user_settings.get("user_stocks", [])
    stock_defaults = {"AAPL": 150.12, "AMZN": 3173.18, "GOOGL": 2742.39, "MSFT": 296.71, "TSLA": 1007.08}

    for stock in stocks:
        stock_prices.append({"stock": stock, "price": stock_defaults.get(stock, 100.00)})
    return stock_prices
