import re
from datetime import datetime, date, timedelta
from typing import Tuple, Optional
from decimal import Decimal, InvalidOperation

class ValidationError(Exception):
    pass

class ProfitValidator:
    DATE_FORMAT = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d/%m',
    ]
    @staticmethod
    def validate_amount(amount):
        if not amount.strip():
            raise ValidationError("Сумма не может быть пустой")
        cleaned = amount.replace(',', '.').replace(' ', '').replace('$', '').replace('₽', '')
        try:
            amount = float(cleaned)
        except ValueError:
            raise ValidationError(f"Некорректная сумма: '{amount}'. Используйте числа (например: 1000 или -500)")

        if amount < -1_000_000:
            raise ValidationError("Сумма слишком маленькая (меньше -1,000,000)")
        if amount > 100_000_000:
            raise ValidationError("Сумма слишком большая (больше 100,000,000)")
        return amount
    @staticmethod
    def validate_date(date_str: str) -> date:
        """
                Валидация даты с поддержкой разных форматов

                Args:
                    date_str: Строка с датой

                Returns:
                    date: Валидная дата

                Raises:
                    ValidationError: Если дата невалидна
                """
        date_str = date_str.lower().strip()
        # Пробуем разные форматы дат
        for date_format in ProfitValidator.DATE_FORMAT:
            try:
                if date_format == "%d.%m":
                    # Для краткого формата добавляем текущий год
                    parsed_date = datetime.strptime(date_str, date_format).replace(year=date.today().year).date()
                else:
                    parsed_date = datetime.strptime(date_str, date_format).date()

                # Проверяем разумные пределы
                today = date.today()
                min_date = today - timedelta(days=5 * 365)  # 5 лет назад
                max_date = today + timedelta(days=30)  # Максимум месяц вперед

                if parsed_date < min_date:
                    raise ValidationError(f"Дата слишком давняя (ранее {min_date.strftime('%d.%m.%Y')})")

                if parsed_date > max_date:
                    raise ValidationError(f"Дата слишком далекая (позже {max_date.strftime('%d.%m.%Y')})")

                return parsed_date

            except ValueError:
                continue

        # Если ни один формат не подошел
        raise ValidationError(
            f"Неподдерживаемый формат даты: '{date_str}'\n"
            f"Поддерживаемые форматы:\n"
            f"• 2024-06-01\n"
            f"• 01.06.2024\n"
            f"• 01.06\n"
        )

    @staticmethod
    def parse_profit_input(text: str) -> Tuple[float, Optional[date]]:
        """
        Парсинг команды добавления прибыли

        Args:
            text: Текст от пользователя

        Returns:
            Tuple[float, Optional[date]]: Сумма и дата (None = сегодня)

        Raises:
            ValidationError: Если ввод невалиден
        """

        if not text.strip():
            raise ValidationError("Введите сумму")

        parts = text.strip().split()

        if len(parts) == 1:
            # Только сумма - используем сегодняшнюю дату
            amount = ProfitValidator.validate_amount(parts[0])
            return amount, None

        elif len(parts) == 2:
            # Сумма и дата
            amount = ProfitValidator.validate_amount(parts[0])
            profit_date = ProfitValidator.validate_date(parts[1])
            return amount, profit_date

        else:
            raise ValidationError(
                "Слишком много параметров.\n"
                "Используйте:\n"
                "• [сумма] - для сегодняшней даты\n"
                "• [сумма] [дата] - для конкретной даты"
            )
