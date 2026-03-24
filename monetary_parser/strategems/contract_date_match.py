import re
from datetime import date, datetime

from budget.base.strategy import Strategy


class ContractDateMarchStrategy(Strategy[date]):
    def __init__(self, text_content: str) -> None:
        self.text_content = text_content
        self.contract_date = None

    def _validate(self) -> None:
        if not self.text_content:
            self._raise(["Текст не может быть пустым."])

        if not isinstance(self.text_content, str):
            self._raise(["Текст должен быть строкой."])

        self.contract_date = re.search(
            r"Дата\s*(?:занлючения|заключения)\s*договора:\s*(\d{2}\.\d{2}\.\d{4})",
            self.text_content,
            re.IGNORECASE,
        )

        if not self.contract_date:
            self._raise(["Текст не содержит информацию о дате."])

    def _start(self) -> date:
        return datetime.strptime(self.contract_date.group(1), "%d.%m.%Y").date()
