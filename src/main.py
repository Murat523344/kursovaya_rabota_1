import json
from pathlib import Path

import pandas as pd

from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday,
)
from src.services import investment_bank, simple_search
from src.views import main_page


def load_transactions() -> pd.DataFrame:
    """Загрузка транзакций из Excel."""
    file_path = Path("data/operations.xlsx")
    return pd.read_excel(file_path)


def main() -> None:
    """Главная функция запуска приложения."""

    print("Программа анализа банковских транзакций\n")

    transactions_df = load_transactions()
    transactions_list = transactions_df.to_dict("records")

    print("=== Главная страница ===")
    print(main_page("2021-12-20 10:00:00"))

    print("\n=== Простой поиск ===")
    result = simple_search("Ozon", transactions_list)
    print(result)

    print("\n=== Инвесткопилка ===")
    invest = investment_bank("2021-12", transactions_list, 50)
    print(f"Сумма накоплений: {invest}")

    print("\n=== Отчет: траты по категории ===")
    report = spending_by_category(transactions_df, "Супермаркеты")
    print(report)

    print("\n=== Отчет: траты по дням недели ===")
    report = spending_by_weekday(transactions_df)
    print(report)

    print("\n=== Отчет: рабочий / выходной день ===")
    report = spending_by_workday(transactions_df)
    print(report)


if __name__ == "__main__":
    main()
