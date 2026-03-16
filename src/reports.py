"""
Модуль для формирования отчетов по транзакциям.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Callable, Any, Dict, List

import pandas as pd

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def report_decorator(arg: Optional[str] = None) -> Callable:
    """
    Декоратор для записи результатов отчета в файл.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Определяем имя файла
            if isinstance(arg, str):
                output_file = arg
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"report_{timestamp}.json"

            # Сохраняем результат
            try:
                if isinstance(result, pd.DataFrame):
                    csv_file = output_file.replace('.json', '.csv')
                    result.to_csv(csv_file, index=False, encoding='utf-8')
                    logger.info(f"Отчет сохранен в {csv_file}")
                else:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    logger.info(f"Отчет сохранен в {output_file}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")

            return result

        return wrapper

    if callable(arg):
        return decorator(arg)
    return decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца.
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    if transactions.empty or 'Дата операции' not in transactions.columns:
        return pd.DataFrame(columns=['Категория', 'Сумма'])

    df = transactions.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True, errors='coerce')

    mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)
    df_filtered = df[mask].copy()

    if df_filtered.empty:
        return pd.DataFrame(columns=['Категория', 'Сумма'])

    category_mask = df_filtered['Категория'] == category
    expenses_mask = df_filtered['Сумма платежа'] < 0
    final_mask = category_mask & expenses_mask

    result_df = df_filtered[final_mask].copy()

    if result_df.empty:
        return pd.DataFrame(columns=['Категория', 'Сумма'])

    result = result_df.groupby('Категория')['Сумма платежа'].sum().abs().reset_index()
    result.columns = ['Категория', 'Сумма']

    return result


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает средние траты по дням недели за последние 3 месяца.
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    days_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    days_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if transactions.empty or 'Дата операции' not in transactions.columns:
        return pd.DataFrame({'День_недели': days_ru, 'Средние_траты': [0.0] * 7})

    df = transactions.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True, errors='coerce')

    mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)
    filtered = df[mask].copy()

    if filtered.empty:
        return pd.DataFrame({'День_недели': days_ru, 'Средние_траты': [0.0] * 7})

    expenses = filtered[filtered['Сумма платежа'] < 0].copy()
    if expenses.empty:
        return pd.DataFrame({'День_недели': days_ru, 'Средние_траты': [0.0] * 7})

    expenses['weekday'] = expenses['Дата операции'].dt.day_name()
    expenses['amount'] = abs(expenses['Сумма платежа'])

    result_data = []
    for en_day, ru_day in zip(days_en, days_ru):
        day_expenses = expenses[expenses['weekday'] == en_day]
        avg = day_expenses['amount'].mean() if not day_expenses.empty else 0.0
        result_data.append({'День_недели': ru_day, 'Средние_траты': avg})

    return pd.DataFrame(result_data)


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает средние траты в рабочие и выходные дни за последние 3 месяца.
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    if transactions.empty or 'Дата операции' not in transactions.columns:
        return pd.DataFrame({'Тип_дня': ['Рабочий', 'Выходной'], 'Средние_траты': [0.0, 0.0]})

    df = transactions.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True, errors='coerce')

    mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)
    filtered = df[mask].copy()

    if filtered.empty:
        return pd.DataFrame({'Тип_дня': ['Рабочий', 'Выходной'], 'Средние_траты': [0.0, 0.0]})

    expenses = filtered[filtered['Сумма платежа'] < 0].copy()
    if expenses.empty:
        return pd.DataFrame({'Тип_дня': ['Рабочий', 'Выходной'], 'Средние_траты': [0.0, 0.0]})

    expenses['weekday'] = expenses['Дата операции'].dt.weekday
    expenses['amount'] = abs(expenses['Сумма платежа'])

    workday_mask = expenses['weekday'] < 5
    weekend_mask = expenses['weekday'] >= 5

    workday_avg = expenses[workday_mask]['amount'].mean() if not expenses[workday_mask].empty else 0.0
    weekend_avg = expenses[weekend_mask]['amount'].mean() if not expenses[weekend_mask].empty else 0.0

    return pd.DataFrame({
        'Тип_дня': ['Рабочий', 'Выходной'],
        'Средние_траты': [workday_avg, weekend_avg]
    })
