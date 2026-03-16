from src.services import investment_bank, profitable_categories

sample_transactions = [
    {
        "Дата операции": "2026-03-01",
        "Категория": "Супермаркеты",
        "Номер карты": "1234",
        "Описание": "Ozon",
        "Сумма платежа": 1712,
        "Сумма операции": 1712,
    },
    {
        "Дата операции": "2026-03-04",
        "Категория": "Переводы",
        "Номер карты": "5678",
        "Описание": "Валерий А.",
        "Сумма платежа": 500,
        "Сумма операции": 500,
    },
]


def test_profitable_categories():
    res = profitable_categories(sample_transactions, 2026, 3)
    assert isinstance(res, dict)
    assert "Супермаркеты" in res


def test_investment_bank():
    res = investment_bank("2026-03", sample_transactions, 50)
    assert isinstance(res, float)
    assert res >= 0
