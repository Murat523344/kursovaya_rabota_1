import pytest

from src import views


@pytest.fixture
def sample_transactions():
    return [
        {
            "Дата операции": "2026-03-01",
            "Сумма платежа": -100,
            "Категория": "Супермаркеты",
            "Номер карты": "1234",
            "Описание": "Ozon",
        },
        {
            "Дата операции": "2026-03-02",
            "Сумма платежа": 500,
            "Категория": "Пополнение_BANK007",
            "Номер карты": "1234",
            "Описание": "Пополнение",
        },
    ]


@pytest.fixture
def user_settings():
    return {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}


def test_main_page(sample_transactions, user_settings):
    res = views.main_page(
        "2026-03-10 12:00:00", sample_transactions, user_settings
    )
    assert "greeting" in res
    assert isinstance(res["cards"], list)
    assert isinstance(res["top_transactions"], list)
    assert isinstance(res["currency_rates"], list)
    assert isinstance(res["stock_prices"], list)


def test_events_page(sample_transactions, user_settings):
    res = views.events_page(
        "2026-03-10 12:00:00",
        sample_transactions,
        range_option="M",
        user_settings=user_settings,
    )
    assert "expenses" in res
    assert "income" in res
    assert isinstance(res["expenses"]["main"], list)
    assert isinstance(res["income"]["main"], list)
