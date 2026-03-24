from django.db import transaction

from budget.base.strategy import Strategy
from monetary_parser.schemas import TransactionListSchema
from transactions.models import Product, Transaction


class BulkCreateTransaction(Strategy):
    def __init__(self, data: TransactionListSchema, product: Product) -> None:
        self.data = data
        self.product = product

    def _validate(self) -> None:
        pass

    def _start(self) -> None:
        with transaction.atomic():
            Transaction.objects.bulk_create(
                [
                    Transaction(product=self.product, **trans.model_dump())
                    for trans in self.data.transactions
                ],
                batch_size=999,
                ignore_conflicts=True,
            )
