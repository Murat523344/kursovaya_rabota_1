"""
Тесты для модуля services.py
"""

import json
import pytest
from src import services


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми транзакциями"""
    return [
        {
            "Дата операции": "2026-03-01",
            "Категория": "Супермаркеты",
            "Сумма операции": 1000.0,
            "Сумма платежа": -1000.0
        },
        {
            "Дата операции": "2026-03-02",
            "Категория": "Рестораны",
            "Сумма операции": 500.0,
            "Сумма платежа": -500.0
        },
        {
            "Дата операции": "2026-03-03",
            "Категория": "Супермаркеты",
            "Сумма операции": 2000.0,
            "Сумма платежа": -2000.0
        },
        {
            "Дата операции": "2026-03-04",
            "Категория": "Транспорт",
            "Сумма операции": 300.0,
            "Сумма платежа": -300.0
        },
        {
            "Дата операции": "2026-03-05",
            "Категория": "Супермаркеты",
            "Сумма операции": 1500.0,
            "Сумма платежа": -1500.0
        },
    ]


def test_profitable_categories_success(sample_transactions):
    """Тест успешного анализа выгодных категорий"""
    result = services.profitable_categories(sample_transactions, 2026, 3)
    res = json.loads(result)

    assert isinstance(res, dict)
    assert len(res) > 0

    # Проверяем что категории сгруппированы
    assert "Супермаркеты" in res
    assert res["Супермаркеты"] > 0


def test_profitable_categories_with_empty_data():
    """Тест с пустыми данными"""
    result = services.profitable_categories([], 2026, 3)
    res = json.loads(result)
    assert res == {}


def test_profitable_categories_different_month(sample_transactions):
    """Тест с месяцем без транзакций"""
    result = services.profitable_categories(sample_transactions, 2026, 4)
    res = json.loads(result)
    assert res == {}


def test_investment_bank_success():
    """Тест успешного расчета инвесткопилки"""
    transactions = [
        {"Дата операции": "2026-03-01", "Сумма операции": 1234.0},
        {"Дата операции": "2026-03-02", "Сумма операции": 567.0},
        {"Дата операции": "2026-03-03", "Сумма операции": 890.0},
    ]

    result = services.investment_bank("2026-03", transactions, 50)
    res = json.loads(result)

    assert isinstance(res, float)
    # Проверяем расчет: (1250-1234) + (600-567) + (900-890) = 16 + 33 + 10 = 59
    assert res == 59.0


def test_investment_bank_different_limits():
    """Тест инвесткопилки с разными лимитами"""
    transactions = [
        {"Дата операции": "2026-03-01", "Сумма операции": 1234.0},
    ]

    # Лимит 10
    result_10 = services.investment_bank("2026-03", transactions, 10)
    assert json.loads(result_10) == 6.0  # 1240 - 1234

    # Лимит 50
    result_50 = services.investment_bank("2026-03", transactions, 50)
    assert json.loads(result_50) == 16.0  # 1250 - 1234

    # Лимит 100
    result_100 = services.investment_bank("2026-03", transactions, 100)
    assert json.loads(result_100) == 66.0  # 1300 - 1234


def test_investment_bank_with_empty_data():
    """Тест инвесткопилки с пустыми данными"""
    result = services.investment_bank("2026-03", [], 50)
    res = json.loads(result)
    assert res == 0.0


def test_investment_bank_wrong_month():
    """Тест инвесткопилки с месяцем без транзакций"""
    transactions = [
        {"Дата операции": "2026-03-01", "Сумма операции": 1234.0},
    ]
    result = services.investment_bank("2026-04", transactions, 50)
    res = json.loads(result)
    assert res == 0.0


def test_investment_bank_only_positive():
    """Тест что учитываются только положительные суммы"""
    transactions = [
        {"Дата операции": "2026-03-01", "Сумма операции": 1234.0},
        {"Дата операции": "2026-03-02", "Сумма операции": -500.0},  # Не должна учитываться
    ]
    result = services.investment_bank("2026-03", transactions, 50)
    res = json.loads(result)
    assert res == 16.0  # Только от первой транзакции
