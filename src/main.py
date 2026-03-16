import json

from src.utils import load_transactions, load_user_settings
from src.views import main_page


def main() -> None:
    """Главная функция для демонстрации работы проекта."""
    print("Программа анализа банковских транзакций")

    print("\n=== Загрузка данных ===")
    transactions = load_transactions("data/operations.xlsx")
    print(f"Загружено транзакций: {len(transactions)}")

    print("\n=== Загрузка настроек ===")
    user_settings = load_user_settings("user_settings.json")
    print(f"Настройки: {user_settings}")

    print("\n=== Главная страница ===")
    result_json = main_page("2021-12-20 10:00:00", transactions, user_settings)

    # Парсим JSON и выводим красиво
    result = json.loads(result_json)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
