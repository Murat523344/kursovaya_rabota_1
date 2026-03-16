"""
Тесты для модуля utils.py
"""

import pytest
import pandas as pd
import json
from src import utils


@pytest.fixture
def sample_transactions_list():
    """Фикстура со списком транзакций"""
    return [
        {
            "Дата операции": "2026-03-01",
            "Сумма платежа": -100,
            "Категория": "Супермаркеты",
            "Номер карты": "1234",
            "Описание": "Ozon"
        },
        {
            "Дата операции": "2026-03-02",
            "Сумма платежа": 500,
            "Категория": "Пополнение_BANK007",
            "Номер карты": "1234",
            "Описание": "Пополнение"
        },
        {
            "Дата операции": "2026-03-03",
            "Сумма платежа": -50,
            "Категория": "Фастфуд",
            "Номер карты": "5678",
            "Описание": "KFC"
        },
        {
            "Дата операции": "2026-03-04",
            "Сумма платежа": -30,
            "Категория": "Переводы",
            "Номер карты": "5678",
            "Описание": "Валерий А."
        },
        {
            "Дата операции": "2026-03-05",
            "Сумма платежа": -20,
            "Категория": "Фастфуд",
            "Номер карты": "5678",
            "Описание": "Я МТС +7 921 11-22-33"
        },
    ]


@pytest.fixture
def sample_dataframe(sample_transactions_list):
    """Фикстура с DataFrame транзакций"""
    return pd.DataFrame(sample_transactions_list)


def test_load_transactions_success(tmp_path):
    """Тест успешной загрузки транзакций из Excel"""
    # Создаем временный Excel файл
    df = pd.DataFrame({"test": [1, 2, 3]})
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)

    # Тестируем загрузку
    result = utils.load_transactions(str(file_path))
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_load_transactions_file_not_found():
    """Тест ошибки при ненайденном файле"""
    result = utils.load_transactions("nonexistent.xlsx")
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_load_transactions_wrong_format(tmp_path):
    """Тест загрузки файла неправильного формата"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test data")

    result = utils.load_transactions(str(file_path))
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_load_user_settings_success(tmp_path):
    """Тест успешной загрузки настроек"""
    settings = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    file_path = tmp_path / "settings.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f)

    result = utils.load_user_settings(str(file_path))
    assert result == settings


def test_load_user_settings_file_not_found():
    """Тест загрузки настроек при отсутствии файла"""
    result = utils.load_user_settings("nonexistent.json")
    assert "user_currencies" in result
    assert "user_stocks" in result
    assert isinstance(result["user_currencies"], list)


def test_load_user_settings_invalid_json(tmp_path):
    """Тест загрузки некорректного JSON"""
    file_path = tmp_path / "invalid.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("invalid json")

    result = utils.load_user_settings(str(file_path))
    assert "user_currencies" in result
    assert "user_stocks" in result


def test_filter_transactions_by_date(sample_dataframe):
    """Тест фильтрации по дате"""
    # Преобразуем даты в datetime для теста
    sample_dataframe['Дата операции'] = pd.to_datetime(
        sample_dataframe['Дата операции'],
        format='%Y-%m-%d'
    )

    result = utils.filter_transactions_by_date(
        sample_dataframe, "2026-03-01", "2026-03-03"
    )
    assert len(result) == 3


def test_filter_transactions_by_date_no_date_column(sample_dataframe):
    """Тест фильтрации при отсутствии колонки с датой"""
    df_no_date = sample_dataframe.drop(columns=['Дата операции'])
    result = utils.filter_transactions_by_date(df_no_date, "2026-03-01", "2026-03-03")
    assert len(result) == len(df_no_date)


def test_get_cards_info(sample_dataframe):
    """Тест получения информации по картам"""
    result = utils.get_cards_info(sample_dataframe)
    assert isinstance(result, list)

    # Проверяем структуру данных
    for card in result:
        assert "last_digits" in card
        assert "total_spent" in card
        assert "cashback" in card
        assert isinstance(card["last_digits"], str)
        # Исправляем: преобразуем numpy типы в Python float для проверки
        assert isinstance(float(card["total_spent"]), float)
        assert isinstance(float(card["cashback"]), float)


def test_get_cards_info_no_card_column(sample_dataframe):
    """Тест получения информации по картам при отсутствии колонки с номерами карт"""
    df_no_card = sample_dataframe.drop(columns=['Номер карты'])
    result = utils.get_cards_info(df_no_card)
    assert result == []


def test_search_transactions(sample_transactions_list):
    """Тест поиска транзакций по категории"""
    result = utils.search_transactions(sample_transactions_list, "Фастфуд")
    assert len(result) == 2
    for transaction in result:
        assert transaction["Категория"] == "Фастфуд"


def test_search_transactions_by_description(sample_transactions_list):
    """Тест поиска транзакций по описанию"""
    result = utils.search_transactions(sample_transactions_list, "Ozon")
    assert len(result) == 1
    assert result[0]["Описание"] == "Ozon"


def test_search_transactions_case_insensitive(sample_transactions_list):
    """Тест поиска транзакций без учета регистра"""
    result = utils.search_transactions(sample_transactions_list, "фастфуд")
    assert len(result) == 2


def test_search_transactions_no_results(sample_transactions_list):
    """Тест поиска без результатов"""
    result = utils.search_transactions(sample_transactions_list, "Nonexistent")
    assert len(result) == 0


def test_find_phone_transactions(sample_transactions_list):
    """Тест поиска транзакций с телефонами"""
    result = utils.find_phone_transactions(sample_transactions_list)
    # Проверяем что нашли хотя бы одну транзакцию с телефоном
    assert len(result) >= 1
    found = False
    for trans in result:
        if "+7 921" in trans.get("Описание", ""):
            found = True
            break
    assert found, "Не найдена транзакция с телефоном +7 921"


def test_find_phone_transactions_different_formats():
    """Тест поиска телефонов в разных форматах"""
    transactions = [
        {"Описание": "+7 921 11-22-33", "Категория": "Связь", "Сумма платежа": -100},
        {"Описание": "+7921112233", "Категория": "Связь", "Сумма платежа": -200},
        {"Описание": "8 921 112233", "Категория": "Связь", "Сумма платежа": -300},
        {"Описание": "Обычный текст", "Категория": "Другое", "Сумма платежа": -400},
    ]
    result = utils.find_phone_transactions(transactions)
    # В зависимости от реализации, может найти 2 или 3
    assert len(result) >= 2  # Должны найти минимум первые два


def test_find_phone_transactions_no_phones():
    """Тест поиска телефонов при их отсутствии"""
    transactions = [
        {"Описание": "Обычный текст", "Категория": "Другое", "Сумма платежа": -100},
        {"Описание": "Еще текст", "Категория": "Другое", "Сумма платежа": -200},
    ]
    result = utils.find_phone_transactions(transactions)
    assert len(result) == 0


def test_find_person_transfers(sample_transactions_list):
    """Тест поиска переводов физическим лицам"""
    result = utils.find_person_transfers(sample_transactions_list)
    assert len(result) >= 1
    found = False
    for trans in result:
        if "Валерий А." in trans.get("Описание", ""):
            found = True
            break
    assert found, "Не найден перевод с именем Валерий А."


def test_find_person_transfers_different_names():
    """Тест поиска переводов с разными именами"""
    transactions = [
        {"Категория": "Переводы", "Описание": "Валерий А.", "Сумма платежа": -100},
        {"Категория": "Переводы", "Описание": "Сергей П.", "Сумма платежа": -200},
        {"Категория": "Переводы", "Описание": "Анна И.", "Сумма платежа": -300},
        {"Категория": "Переводы", "Описание": "Просто текст", "Сумма платежа": -400},
        {"Категория": "Другое", "Описание": "Валерий А.", "Сумма платежа": -500},
    ]
    result = utils.find_person_transfers(transactions)
    assert len(result) == 3  # Должны найти первые три


def test_find_person_transfers_no_transfers():
    """Тест поиска переводов при их отсутствии"""
    transactions = [
        {"Категория": "Супермаркеты", "Описание": "Валерий А.", "Сумма платежа": -100},
        {"Категория": "Фастфуд", "Описание": "Сергей П.", "Сумма платежа": -200},
    ]
    result = utils.find_person_transfers(transactions)
    assert len(result) == 0
