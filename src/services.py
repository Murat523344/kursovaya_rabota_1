"""
Модуль для сервисов анализа транзакций.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


def profitable_categories(transactions: List[Dict], year: int, month: int) -> str:
    """
    Анализирует выгодные категории для кешбэка.

    Args:
        transactions: Список транзакций
        year: Год для анализа
        month: Месяц для анализа

    Returns:
        JSON-строка с анализом категорий
    """
    result: Dict[str, float] = {}

    for transaction in transactions:
        # Проверяем дату
        date_str = transaction.get("Дата операции", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        if date.year == year and date.month == month:
            category = transaction.get("Категория", "")
            amount = abs(float(transaction.get("Сумма платежа", 0)))

            if amount > 0:
                cashback = amount * 0.01  # 1% кешбэк
                result[category] = result.get(category, 0) + cashback

    return json.dumps(result, ensure_ascii=False)


def investment_bank(month: str, transactions: List[Dict], limit: int) -> str:
    """
    Рассчитывает сумму для инвесткопилки.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Лимит округления (10, 50, 100)

    Returns:
        JSON-строка с суммой накоплений
    """
    year, month_num = map(int, month.split("-"))
    total = 0.0

    for transaction in transactions:
        # Проверяем дату
        date_str = transaction.get("Дата операции", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        if date.year == year and date.month == month_num:
            # Берем сумму операции (расходы)
            amount = float(transaction.get("Сумма операции", 0))
            if amount > 0:  # Только положительные суммы
                rounded = ((amount + limit - 1) // limit) * limit
                total += rounded - amount

    return json.dumps(total, ensure_ascii=False)
