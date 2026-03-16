"""
Главный модуль для демонстрации всех функций приложения.
"""

import json
import logging
from src.views import main_page, events_page
from src.utils import load_transactions, load_user_settings
from src.services import profitable_categories, investment_bank
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Главная функция для демонстрации работы проекта."""
    print("=" * 50)
    print("ПРОГРАММА АНАЛИЗА БАНКОВСКИХ ТРАНЗАКЦИЙ")
    print("=" * 50)

    # Загружаем данные
    print("\n📁 Загрузка данных...")
    transactions = load_transactions("data/operations.xlsx")
    print(f"✅ Загружено транзакций: {len(transactions)}")

    # Загружаем настройки
    print("\n⚙️ Загрузка настроек пользователя...")
    user_settings = load_user_settings("user_settings.json")
    print(f"✅ Настройки: {user_settings}")

    # Демонстрация главной страницы
    print("\n" + "=" * 50)
    print("🏠 ГЛАВНАЯ СТРАНИЦА")
    print("=" * 50)
    try:
        result_main = main_page("2021-12-20 10:00:00", transactions, user_settings)
        data_main = json.loads(result_main)
        print(f"👋 Приветствие: {data_main['greeting']}")
        print(f"💳 Карт найдено: {len(data_main['cards'])}")
        print(f"💰 Топ-5 транзакций: {len(data_main['top_transactions'])}")
        print(f"💵 Курсы валют: {data_main['currency_rates']}")
        print(f"📈 Цены акций: {data_main['stock_prices'][:2]}...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # Демонстрация страницы событий
    print("\n" + "=" * 50)
    print("📊 СТРАНИЦА СОБЫТИЙ")
    print("=" * 50)
    try:
        result_events = events_page("2021-12-20 10:00:00", transactions, "M", user_settings)
        data_events = json.loads(result_events)
        print(f"💸 Расходы: {data_events['expenses']['total_amount']}")
        print(f"💰 Доходы: {data_events['income']['total_amount']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # Демонстрация сервиса инвесткопилки
    print("\n" + "=" * 50)
    print("🐷 ИНВЕСТКОПИЛКА")
    print("=" * 50)
    try:
        # Преобразуем DataFrame в список словарей для сервиса
        transactions_list = transactions.to_dict('records') if hasattr(transactions, 'to_dict') else transactions
        inv_result = investment_bank("2021-12", transactions_list, 50)
        print(f"💰 Накоплено за декабрь 2021: {inv_result} руб.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # Демонстрация отчета по категории
    print("\n" + "=" * 50)
    print("📈 ОТЧЕТ: ТРАТЫ ПО КАТЕГОРИИ")
    print("=" * 50)
    try:
        category_report = spending_by_category(transactions, "Супермаркеты", "2021-12-20")
        print(f"📊 Траты на супермаркеты за 3 месяца:")
        print(category_report)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("\n" + "=" * 50)
    print("✅ РАБОТА ПРОГРАММЫ ЗАВЕРШЕНА")
    print("=" * 50)


if __name__ == "__main__":
    main()
