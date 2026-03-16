import pytest

from src import utils


@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "2026-03-01", "Сумма платежа": -100, "Категория": "Супермаркеты",
         "Номер карты": "1234", "Описание": "Ozon"},
        {"Дата операции": "2026-03-02", "Сумма платежа": 500, "Категория": "Пополнение_BANK007",
         "Номер карты": "1234", "Описание": "Пополнение"},
        {"Дата операции": "2026-03-03", "Сумма платежа": -50, "Категория": "Фастфуд",
         "Номер карты": "5678", "Описание": "KFC"},
        {"Дата операции": "2026-03-04", "Сумма платежа": -30, "Категория": "Переводы",
         "Номер карты": "5678", "Описание": "Валерий А."},
        {"Дата операции": "2026-03-05", "Сумма платежа": -20, "Категория": "Фастфуд",
         "Номер карты": "5678", "Описание": "Я МТС +7 921 11-22-33"},
    ]


def test_search_transactions(sample_transactions):
    result = utils.search_transactions(sample_transactions, "Фастфуд")
    assert len(result) == 2


def test_find_phone_transactions(sample_transactions):
    result = utils.find_phone_transactions(sample_transactions)
    assert len(result) == 1
    assert "+7 921" in result[0]["Описание"]


def test_find_person_transfers(sample_transactions):
    result = utils.find_person_transfers(sample_transactions)
    assert len(result) == 1
    assert "Валерий А." in result[0]["Описание"]
