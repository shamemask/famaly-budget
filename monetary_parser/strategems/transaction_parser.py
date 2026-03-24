import logging
import re
from datetime import datetime
from decimal import Decimal

from django.utils.timezone import make_aware

from budget.base.strategy import Strategy
from monetary_parser.schemas import TransactionListSchema, TransactionSchema
from monetary_parser.strategems.bulk_create_transaction import BulkCreateTransaction
from transactions.models import Product, Transaction

logger = logging.getLogger(__name__)

TINKOFF_ROW_PATTERN = r"(\d{2}\.\d{2}\.\d{4})\s+(\d{2}\.\d{2}\.\d{4})\s+([+-]?\s*\d[\s\d,.]*)\s*₽\s+([+-]?\s*\d[\s\d,.]*)\s*₽\s+(.+?)\s+(\d{4}|\W)$"


class TransactionParserStrategy(Strategy):
    def __init__(self, text_content: str, product: Product) -> None:
        self.text_content = text_content
        self.product = product

    def _validate(self) -> None:
        if not isinstance(self.text_content, str):
            self._raise(["Текст должен быть строкой."])

    def _start(self) -> None:
        lines = self.text_content.split("\n")
        transactions = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if re.match(r"\d{2}\.\d{2}\.\d{4}", line):
                match = re.match(TINKOFF_ROW_PATTERN, line)
                if match:
                    (
                        operation_date,
                        description_date,
                        amount_str,
                        _,
                        description,
                        card_last_four,
                    ) = match.groups()
                    i += 1
                    time_parts = []
                    if i + 1 < len(lines) and re.match(r"\d{2}:\d{2}", lines[i]):
                        time_line = lines[i].strip()
                        time_match = re.match(r"(\d{2}:\d{2})\s+(\d{2}:\d{2})", time_line)
                        if time_match:
                            time_parts = time_match.groups()
                            description += time_line.split(time_parts[-1])[-1]

                            i += 1
                            line = lines[i].strip()
                            while not re.match(r"\d{2}\.\d{2}\.\d{4}", line) and i + 1 < len(lines):
                                if not line.startswith("АО «ТБанк»"):
                                    description += " " + line
                                i += 1
                                line = lines[i].strip()
                        else:
                            logger.warning("Некорректный формат времени.")
                            i += 1
                    else:
                        logger.warning("Время не найдено для строки.")
                        i += 1

                    try:
                        if time_parts:
                            operation_datetime = make_aware(
                                datetime.strptime(
                                    f"{operation_date} {time_parts[0]}",
                                    "%d.%m.%Y %H:%M",
                                ),
                            )
                            description_datetime = make_aware(
                                datetime.strptime(
                                    f"{description_date} {time_parts[1]}",
                                    "%d.%m.%Y %H:%M",
                                ),
                            )
                        else:
                            operation_datetime = make_aware(
                                datetime.strptime(operation_date, "%d.%m.%Y"),
                            )
                            description_datetime = make_aware(
                                datetime.strptime(description_date, "%d.%m.%Y"),
                            )

                        amount_clean = amount_str.replace(" ", "").replace(",", ".")
                        amount = Decimal(amount_clean)

                        if not re.match(r"^\d{4}$", card_last_four):
                            logger.warning("Некорректный формат номера карты")
                            continue

                        # Проверка уникальности
                        if (
                            self.product
                            and Transaction.objects.filter(
                                product=self.product,
                                operation_datetime=operation_datetime,
                                amount=amount,
                                card_last_four=card_last_four,
                            ).exists()
                        ):
                            continue

                        transaction = TransactionSchema(
                            operation_datetime=operation_datetime,
                            description_date=description_datetime,
                            amount=amount,
                            description=description,
                            card_last_four=card_last_four,
                        )
                        transactions.append(transaction)
                    except ValueError as e:
                        message = f"Ошибка обработки транзакции: {line}, ошибка: {e!s}"
                        logger.warning(message)
                        continue
                else:
                    logger.warning("Некорректная строка транзакции")
                    i += 1
            else:
                i += 1
        transactions_list = TransactionListSchema(transactions=transactions)

        if transactions_list and self.product:
            try:
                BulkCreateTransaction(transactions_list, product=self.product).start()
            except Exception as e:
                message = f"Ошибка сохранения транзакций: {e!s}"
                logger.exception(message)
