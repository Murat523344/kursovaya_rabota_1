import logging
import re

import pandas as pd
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def read_transactions(file_path: str) -> pd.DataFrame:
    """Чтение транзакций из Excel с безопасной обработкой дат."""
    try:
        df = pd.read_excel(file_path)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], errors="coerce", dayfirst=True)
        return df
    except Exception as e:
        logger.error("Ошибка при чтении файла: %s", e)
        raise


def get_currency_rates(currencies: list) -> list:
    """Получение курса валют через API."""
    rates = []
    for currency in currencies:
        try:
            response = requests.get(f"https://api.exchangerate.host/latest?base=RUB&symbols={currency}")
            data = response.json()
            rates.append({"currency": currency, "rate": round(1 / data["rates"][currency], 2)})
        except Exception as e:
            logger.warning("Ошибка получения курса %s: %s", currency, e)
            rates.append({"currency": currency, "rate": None})
    return rates


def get_stock_prices(stocks: list) -> list:
    """Получение цен акций через Yahoo Finance API."""
    prices = []
    for stock in stocks:
        try:
            response = requests.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock}")
            data = response.json()
            price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
            prices.append({"stock": stock, "price": round(price, 2)})
        except Exception as e:
            logger.warning("Ошибка получения цены акции %s: %s", stock, e)
            prices.append({"stock": stock, "price": None})
    return prices


def search_transactions(transactions: list, query: str) -> list:
    """Поиск транзакций по описанию или категории."""
    return [
        t for t in transactions
        if query.lower() in str(t.get("Описание", "")).lower()
        or query.lower() in str(t.get("Категория", "")).lower()
    ]


def find_phone_transactions(transactions: list) -> list:
    """Поиск транзакций с телефонами."""
    phone_regex = re.compile(r"\+7[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}")
    return [t for t in transactions if phone_regex.search(str(t.get("Описание", "")))]


def find_person_transfers(transactions: list) -> list:
    """Поиск переводов физическим лицам."""
    transfer_regex = re.compile(r"[А-ЯЁ][а-яё]+ [А-Я]\.")
    return [
        t for t in transactions
        if (
                t.get("Категория") == "Переводы"
                and transfer_regex.search(str(t.get("Описание", "")))
        )
    ]
