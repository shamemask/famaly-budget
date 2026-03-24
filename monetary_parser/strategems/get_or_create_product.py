from django.db import transaction

from budget.base.strategy import Strategy
from monetary_parser.schemas import ProductSchema
from transactions.models import Client, Product


class GetOrCreateProductStrategy(Strategy[Product]):
    def __init__(self, data: ProductSchema, client: Client) -> None:
        self.data = data
        self.client = client

    def _validate(self) -> None:
        pass

    def _start(self) -> Product:
        with transaction.atomic():
            product, _ = Product.objects.get_or_create(
                contract_number=self.data.contract_number,
                defaults={
                    "client": self.client,
                    "contract_date": self.data.contract_date,
                    "account_number": self.data.account_number,
                },
            )

            return product
