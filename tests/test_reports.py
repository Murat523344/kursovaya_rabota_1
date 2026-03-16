"""
Тесты для модуля reports.py
"""

import pytest
import pandas as pd
import json
import os
from datetime import datetime
from src import reports


@pytest.fixture
def sample_dataframe():
    """Фикстура с DataFrame транзакций"""
    data = {
        'Дата операции': pd.date_range(start='2026-01-01', periods=100, freq='D'),
        'Категория': ['Супермаркеты'] * 30 + ['Рестораны'] * 30 + ['Транспорт'] * 40,
        'Сумма платежа': [-1000] * 30 + [-500] * 30 + [-300] * 40,
        'Описание': ['Покупка'] * 100
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_file(tmp_path):
    """Фикстура для временного файла"""
    return tmp_path / "test_report.json"


def test_spending_by_category_success(sample_dataframe):
    """Тест успешного получения трат по категории"""
    result = reports.spending_by_category(
        sample_dataframe,
        "Супермаркеты",
        "2026-03-15"
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'Категория' in result.columns
    assert 'Сумма' in result.columns


def test_spending_by_category_without_date(sample_dataframe):
    """Тест получения трат по категории без указания даты"""
    result = reports.spending_by_category(
        sample_dataframe,
        "Супермаркеты"
    )
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_wrong_category(sample_dataframe):
    """Тест с несуществующей категорией"""
    result = reports.spending_by_category(
        sample_dataframe,
        "Nonexistent",
        "2026-03-15"
    )
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_spending_by_weekday_success(sample_dataframe):
    """Тест успешного получения трат по дням недели"""
    result = reports.spending_by_weekday(
        sample_dataframe,
        "2026-03-15"
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'День_недели' in result.columns
    assert 'Средние_траты' in result.columns


def test_spending_by_weekday_without_date(sample_dataframe):
    """Тест получения трат по дням недели без указания даты"""
    result = reports.spending_by_weekday(sample_dataframe)
    assert isinstance(result, pd.DataFrame)


def test_spending_by_weekday_empty_data():
    """Тест с пустыми данными"""
    empty_df = pd.DataFrame()
    result = reports.spending_by_weekday(empty_df, "2026-03-15")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_workday_success(sample_dataframe):
    """Тест успешного получения трат в рабочие/выходные дни"""
    result = reports.spending_by_workday(
        sample_dataframe,
        "2026-03-15"
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'Тип_дня' in result.columns
    assert 'Средние_траты' in result.columns


def test_spending_by_workday_without_date(sample_dataframe):
    """Тест получения трат в рабочие/выходные дни без указания даты"""
    result = reports.spending_by_workday(sample_dataframe)
    assert isinstance(result, pd.DataFrame)


def test_spending_by_workday_empty_data():
    """Тест с пустыми данными"""
    empty_df = pd.DataFrame()
    result = reports.spending_by_workday(empty_df, "2026-03-15")
    assert isinstance(result, pd.DataFrame)


def test_report_decorator_default_filename(temp_file):
    """Тест декоратора с именем файла по умолчанию"""

    @reports.report_decorator
    def test_func():
        return {"test": "data"}

    original_dir = os.getcwd()
    os.chdir(temp_file.parent)

    try:
        result = test_func()
        assert result == {"test": "data"}

        files = os.listdir()
        report_files = [f for f in files if f.startswith('report_') and f.endswith('.json')]
        assert len(report_files) > 0
    finally:
        os.chdir(original_dir)


def test_report_decorator_custom_filename(temp_file):
    """Тест декоратора с пользовательским именем файла"""

    @reports.report_decorator(str(temp_file))
    def test_func():
        return {"test": "data"}

    result = test_func()
    assert result == {"test": "data"}
    assert temp_file.exists()


def test_report_decorator_with_dataframe(sample_dataframe, temp_file):
    """Тест декоратора с возвратом DataFrame"""

    @reports.report_decorator(str(temp_file))
    def test_func():
        return sample_dataframe

    result = test_func()
    assert isinstance(result, pd.DataFrame)

    csv_file = str(temp_file).replace('.json', '.csv')
    file_exists = temp_file.exists() or os.path.exists(csv_file)
    assert file_exists


def test_decorator_chaining(sample_dataframe, temp_file):
    """Тест цепочки декораторов"""

    @reports.report_decorator(str(temp_file))
    def test_func():
        return reports.spending_by_category(sample_dataframe, "Супермаркеты")

    result = test_func()
    assert isinstance(result, pd.DataFrame)

    csv_file = str(temp_file).replace('.json', '.csv')
    file_exists = temp_file.exists() or os.path.exists(csv_file)
    assert file_exists


from unittest.mock import patch, MagicMock


def test_spending_by_category_with_mock():
    """Тест отчета по категориям с mock DataFrame"""
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.__getitem__.return_value = mock_df
    mock_df.__setitem__.return_value = None

    mock_result = MagicMock()
    mock_result.empty = False

    with patch('pandas.to_datetime', return_value=MagicMock()):
        with patch.object(mock_df, 'copy', return_value=mock_df):
            with patch.object(mock_df, 'loc', return_value=mock_result):
                result = reports.spending_by_category(mock_df, "Супермаркеты", "2026-03-15")

                assert isinstance(result, pd.DataFrame) or hasattr(result, 'empty')


def test_report_decorator_with_patch():
    """Тест декоратора с patch для файловой системы"""
    mock_result = {"test": "data"}

    with patch('builtins.open', MagicMock()) as mock_open:
        with patch('json.dump') as mock_json_dump:
            @reports.report_decorator("test.json")
            def test_func():
                return mock_result

            result = test_func()

            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()
            assert result == mock_result
