import re

from budget.base.strategy import Strategy


class AccountNumberMarchStrategy(Strategy[str]):
    def __init__(self, text_content: str) -> None:
        self.text_content = text_content
        self.account_number = None

    def _validate(self) -> None:
        if not self.text_content:
            self._raise(["Текст не может быть пустым."])

        if not isinstance(self.text_content, str):
            self._raise(["Текст должен быть строкой."])

        self.account_number = re.search(
            r"Номер\s*(?:дицевого|лицевого)\s*счета:\s*(.*?)(?:\s*Движение\s*средств|\s*\|)",
            self.text_content,
            re.DOTALL,
        )

        if not self.account_number:
            self._raise(["Текст не содержит информацию о номере счета."])

    def _start(self) -> str:
        return self.account_number.group(1).strip()
