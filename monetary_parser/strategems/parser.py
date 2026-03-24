import logging
from io import BytesIO
from typing import NoReturn

import pdfplumber

from budget.base.strategy import Strategy
from monetary_parser.schemas import ProductSchema
from monetary_parser.strategems.account_number_match import AccountNumberMarchStrategy
from monetary_parser.strategems.contract_date_match import ContractDateMarchStrategy
from monetary_parser.strategems.contract_number_match import ContractNumberMarchStrategy
from monetary_parser.strategems.get_or_create_client import GetOrCreateClient
from monetary_parser.strategems.get_or_create_product import GetOrCreateProductStrategy
from monetary_parser.strategems.tinkoff_client_match import TinkoffClientMarch
from monetary_parser.strategems.transaction_parser import TransactionParserStrategy

logger = logging.getLogger(__name__)

SEP = ":::"


class ParserStrategy(Strategy):
    def __init__(self, file_content: bytes) -> None:
        self.file_content = file_content

    def parse(self) -> NoReturn:
        raise NotImplementedError

    def _validate(self) -> None:
        if not isinstance(self.file_content, bytes):
            self._raise(["Текст должен быть строкой."])

    def plumber(self) -> str:
        text_content = ""
        with pdfplumber.open(BytesIO(self.file_content)) as pdf:
            for page in pdf.pages:
                # Извлечение текста
                text = page.extract_text()
                if text:
                    text_content += text + SEP

        return text_content

    def _start(self) -> None:
        text_content = self.plumber()

        client_march_strategy = TinkoffClientMarch(text_content)
        client_schema = client_march_strategy.start()

        client_strategy = GetOrCreateClient(client_schema)
        client = client_strategy.start()

        contract_date_strategy = ContractDateMarchStrategy(text_content)
        contract_date = contract_date_strategy.start()

        contract_number_strategy = ContractNumberMarchStrategy(text_content)
        contract_number = contract_number_strategy.start()

        account_number_strategy = AccountNumberMarchStrategy(text_content)
        account_number = account_number_strategy.start()

        if client and contract_number:
            product_strategy = GetOrCreateProductStrategy(
                ProductSchema(
                    contract_date=contract_date,
                    contract_number=contract_number,
                    account_number=account_number,
                ),
                client=client,
            )
            product = product_strategy.start()

            transactions_strategy = TransactionParserStrategy(text_content, product)
            transactions_strategy.start()
        else:
            logger.warning("Продукт не найден в тексте.")
