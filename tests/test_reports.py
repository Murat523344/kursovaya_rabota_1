import pandas as pd
import pytest

from src import reports


@pytest.fixture
def df_transactions():
    data = [
        {"Дата операции": "2026-03-01", "Сумма платежа": -100, "Категория": "Супермаркеты"},
        {"Дата операции": "2026-03-02", "Сумма платежа": -50, "Категория": "Фастфуд"},
        {"Дата операции": "2026-03-03", "Сумма платежа": 500, "Категория": "Пополнение_BANK007"},
        {"Дата операции": "2026-03-04", "Сумма платежа": -30, "Категория": "Переводы"},
    ]
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


def test_spending_by_category(df_transactions):
    res = reports.spending_by_category(df_transactions, "Супермаркеты")
    assert res["category"] == "Супермаркеты"
    assert isinstance(res["total_spent"], (int, float))


def test_spending_by_weekday(df_transactions):
    res = reports.spending_by_weekday(df_transactions)
    assert isinstance(res, dict)
    assert all(isinstance(v, float) for v in res.values())


def test_spending_by_workday(df_transactions):
    res = reports.spending_by_workday(df_transactions)
    assert "workday" in res and "weekend" in res
    assert isinstance(res["workday"], float)
    assert isinstance(res["weekend"], float)
