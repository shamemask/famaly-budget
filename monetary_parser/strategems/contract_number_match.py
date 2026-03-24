import re

from budget.base.strategy import Strategy


class ContractNumberMarchStrategy(Strategy[str]):
    def __init__(self, text_content: str) -> None:
        self.text_content = text_content
        self.contract_number = None

    def _validate(self) -> None:
        if not self.text_content:
            self._raise(["Текст не может быть пустым."])

        if not isinstance(self.text_content, str):
            self._raise(["Текст должен быть строкой."])

        self.contract_number = re.search(r"Номер\s*договора:\s*(\d+)", self.text_content)

        if not self.contract_number:
            self._raise(["Текст не содержит информацию о номере договора."])

    def _start(self) -> str:
        return self.contract_number.group(1).strip()
