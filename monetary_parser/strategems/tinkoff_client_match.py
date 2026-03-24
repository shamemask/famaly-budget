import re

from budget.base.strategy import Strategy
from monetary_parser.schemas import ClientSchema


class TinkoffClientMarch(Strategy[ClientSchema]):
    def __init__(self, text_content: str) -> None:
        self.text_content = text_content
        self.client_match = None

    def _validate(self) -> None:
        if not self.text_content:
            self._raise(["Текст не может быть пустым."])

        if not isinstance(self.text_content, str):
            self._raise(["Текст должен быть строкой."])

        self.client_match = re.search(
            r"([А-Яа-я\s]+?)\s*(?:Аррес|Адрес)\s*места\s*жительства:\s*(.*?)\s*(?:Дата|О\s*продукте)",
            self.text_content,
            re.DOTALL | re.IGNORECASE,
        )

        if not self.client_match:
            self._raise(["Текст не содержит информацию о клиенте."])

    def _start(self) -> ClientSchema:
        full_name = self.client_match.group(1).strip()
        address = self.client_match.group(2).strip()

        return ClientSchema.model_validate({"full_name": full_name, "address": address})
