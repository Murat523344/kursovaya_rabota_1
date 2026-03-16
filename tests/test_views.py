"""
Тесты для модуля views.py
"""

import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src import views


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми транзакциями"""
    return [
        {
            'Дата операции': '01.03.2026',
            'Категория': 'Супермаркеты',
            'Номер карты': '*1234',
            'Описание': 'Ozon',
            'Сумма платежа': -1000.0
        },
        {
            'Дата операции': '02.03.2026',
            'Категория': 'Пополнение_BANK007',
            'Номер карты': '*1234',
            'Описание': 'Пополнение',
            'Сумма платежа': 50000.0
        },
        {
            'Дата операции': '05.03.2026',
            'Категория': 'Фастфуд',
            'Номер карты': '*5678',
            'Описание': 'Я МТС +7 921 11-22-33',
            'Сумма платежа': -500.0
        },
        {
            'Дата операции': '10.03.2026',
            'Категория': 'Переводы',
            'Номер карты': '*5678',
            'Описание': 'Валерий А.',
            'Сумма платежа': -300.0
        }
    ]


@pytest.fixture
def user_settings():
    """Фикстура с настройками пользователя"""
    return {
        'user_currencies': ['USD', 'EUR'],
        'user_stocks': ['AAPL', 'GOOGL']
    }


def test_convert_to_dataframe_with_list(sample_transactions):
    """Тест конвертации списка в DataFrame"""
    result = views._convert_to_dataframe(sample_transactions)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_transactions)


def test_convert_to_dataframe_with_dataframe(sample_transactions):
    """Тест конвертации DataFrame в DataFrame"""
    df = pd.DataFrame(sample_transactions)
    result = views._convert_to_dataframe(df)
    assert isinstance(result, pd.DataFrame)
    assert result is df


def test_main_page_success(sample_transactions, user_settings):
    """Тест успешного выполнения главной страницы"""
    res_json = views.main_page(
        "2026-03-10 12:00:00", sample_transactions, user_settings
    )

    res = json.loads(res_json)
    assert "error" not in res
    assert "greeting" in res
    assert "cards" in res
    assert "top_transactions" in res
    assert "currency_rates" in res
    assert "stock_prices" in res


def test_main_page_different_times(sample_transactions, user_settings):
    """Тест приветствия в разное время суток"""
    # Ночь (0-5)
    res_night = json.loads(views.main_page("2026-03-10 03:00:00", sample_transactions, user_settings))
    assert res_night["greeting"] == "Доброй ночи"

    # Утро (5-12)
    res_morning = json.loads(views.main_page("2026-03-10 08:00:00", sample_transactions, user_settings))
    assert res_morning["greeting"] == "Доброе утро"

    # День (12-18)
    res_day = json.loads(views.main_page("2026-03-10 14:00:00", sample_transactions, user_settings))
    assert res_day["greeting"] == "Добрый день"

    # Вечер (18-23)
    res_evening = json.loads(views.main_page("2026-03-10 20:00:00", sample_transactions, user_settings))
    assert res_evening["greeting"] == "Добрый вечер"


def test_main_page_with_empty_data(user_settings):
    """Тест главной страницы с пустыми данными"""
    res_json = views.main_page("2026-03-10 12:00:00", [], user_settings)
    res = json.loads(res_json)
    assert "error" not in res
    assert res["cards"] == []
    assert res["top_transactions"] == []


def test_main_page_cards_info(sample_transactions, user_settings):
    """Тест информации по картам"""
    res_json = views.main_page("2026-03-10 12:00:00", sample_transactions, user_settings)
    res = json.loads(res_json)

    for card in res["cards"]:
        assert "last_digits" in card
        assert "total_spent" in card
        assert "cashback" in card
        assert card["last_digits"] in ["1234", "5678"]
        assert isinstance(card["total_spent"], (int, float))
        assert isinstance(card["cashback"], (int, float))


def test_main_page_currency_rates(sample_transactions, user_settings):
    """Тест курсов валют"""
    res_json = views.main_page("2026-03-10 12:00:00", sample_transactions, user_settings)
    res = json.loads(res_json)

    assert len(res["currency_rates"]) == len(user_settings["user_currencies"])
    for rate in res["currency_rates"]:
        assert "currency" in rate
        assert "rate" in rate
        assert rate["currency"] in user_settings["user_currencies"]


def test_main_page_stock_prices(sample_transactions, user_settings):
    """Тест цен акций"""
    res_json = views.main_page("2026-03-10 12:00:00", sample_transactions, user_settings)
    res = json.loads(res_json)

    assert len(res["stock_prices"]) == len(user_settings["user_stocks"])
    for stock in res["stock_prices"]:
        assert "stock" in stock
        assert "price" in stock
        assert stock["stock"] in user_settings["user_stocks"]


def test_events_page_success(sample_transactions, user_settings):
    """Тест успешного выполнения страницы событий"""
    res_json = views.events_page(
        "2026-03-10 12:00:00",
        sample_transactions,
        range_option="M",
        user_settings=user_settings,
    )

    res = json.loads(res_json)
    assert "error" not in res
    assert "expenses" in res
    assert "income" in res
    assert "currency_rates" in res
    assert "stock_prices" in res


def test_events_page_different_ranges(sample_transactions, user_settings):
    """Тест страницы событий с разными диапазонами"""
    # Неделя
    res_week = json.loads(views.events_page(
        "2026-03-10 12:00:00", sample_transactions, "W", user_settings
    ))
    assert "expenses" in res_week

    # Месяц
    res_month = json.loads(views.events_page(
        "2026-03-10 12:00:00", sample_transactions, "M", user_settings
    ))
    assert "expenses" in res_month

    # Год
    res_year = json.loads(views.events_page(
        "2026-03-10 12:00:00", sample_transactions, "Y", user_settings
    ))
    assert "expenses" in res_year

    # Все данные
    res_all = json.loads(views.events_page(
        "2026-03-10 12:00:00", sample_transactions, "ALL", user_settings
    ))
    assert "expenses" in res_all


def test_events_page_with_empty_data(user_settings):
    """Тест страницы событий с пустыми данными"""
    res_json = views.events_page(
        "2026-03-10 12:00:00",
        [],
        range_option="M",
        user_settings=user_settings,
    )

    res = json.loads(res_json)
    assert "error" not in res
    assert res["expenses"]["total_amount"] == 0
    assert res["income"]["total_amount"] == 0


def test_events_page_without_settings(sample_transactions):
    """Тест страницы событий без настроек пользователя"""
    res_json = views.events_page(
        "2026-03-10 12:00:00",
        sample_transactions,
        range_option="M",
        user_settings=None,
    )

    res = json.loads(res_json)
    assert "error" not in res
    assert "currency_rates" in res
    assert "stock_prices" in res


def test_get_currency_rates(user_settings):
    """Тест получения курсов валют"""
    rates = views._get_currency_rates(user_settings)
    assert len(rates) == len(user_settings["user_currencies"])
    for rate in rates:
        assert "currency" in rate
        assert "rate" in rate


def test_get_stock_prices(user_settings):
    """Тест получения цен акций"""
    prices = views._get_stock_prices(user_settings)
    assert len(prices) == len(user_settings["user_stocks"])
    for price in prices:
        assert "stock" in price
        assert "price" in price


def test_main_page_with_mock():
    """Тест главной страницы с использованием mock"""
    import json
    from unittest.mock import patch, MagicMock

    # Создаём тестовые транзакции с правильными датами
    test_transactions = [
        {'Дата операции': '01.03.2026', 'Сумма платежа': -100,
         'Категория': 'Супермаркеты', 'Номер карты': '*1234'},
        {'Дата операции': '15.03.2026', 'Сумма платежа': -50,
         'Категория': 'Фастфуд', 'Номер карты': '*1234'},
    ]

    user_settings = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

    # Создаём моки
    mock_rates = MagicMock()
    mock_rates.return_value = [{"currency": "USD", "rate": 73.21}]

    mock_stocks = MagicMock()
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.12}]

    # Патчим функции
    with patch('src.views._get_currency_rates', mock_rates):
        with patch('src.views._get_stock_prices', mock_stocks):
            # Вызываем функцию
            result = views.main_page("2026-03-15 12:00:00", test_transactions, user_settings)

            # Проверяем что результат получен
            assert isinstance(result, str)
            data = json.loads(result)
            assert "greeting" in data
            assert "cards" in data
