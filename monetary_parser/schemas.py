from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ClientSchema(BaseModel):
    """
    Схема клиента банка.

    Attributes:
        full_name: str - ФИО клиента.
        address: str - адрес клиента.

    """

    full_name: str
    address: str


class ProductSchema(BaseModel):
    """
    Схема Продукта от банка.

    Attributes:
        contract_date: date - Дата договора.
        contract_number: str - Номер телефона.
        account_number: str - Номер счёта.

    """

    contract_date: date
    contract_number: str
    account_number: str


class TransactionSchema(BaseModel):
    """
    Схема Транзакций в банке.

    Attributes:
        operation_datetime: datetime - Дата и время операции (формат: DD.MM.YYYY HH:MM)
        description_date: datetime - Дата и время описания (формат: DD.MM.YYYY HH:MM)
        amount: Decimal - Сумма транзакции (отрицательная для списания)
        description: str - Описание транзакции
        card_last_four: str - Последние 4 цифры карты (4 цифры)

    """

    operation_datetime: datetime | None = Field(
        description="Дата и время операции (формат: DD.MM.YYYY HH:MM)",
    )
    description_date: datetime | None = Field(
        description="Дата и время описания (формат: DD.MM.YYYY HH:MM)",
    )
    amount: Decimal | None = Field(
        max_digits=10,
        decimal_places=2,
        description="Сумма транзакции (отрицательная для списания)",
    )

    description: str | None = Field(description="Описание транзакции")
    card_last_four: str | None = Field(description="Последние 4 цифры карты (4 цифры)")


class TransactionListSchema(BaseModel):
    """
    Схема Списка транзакций от банка.

    Attributes:
        List[TransactionSchema] - Список транзакций.

    """

    transactions: list[TransactionSchema] = Field(description="Список транзакций")
