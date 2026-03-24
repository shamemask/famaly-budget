from django.db import transaction

from budget.base.strategy import Strategy
from monetary_parser.schemas import ClientSchema
from transactions.models import Client


class GetOrCreateClient(Strategy[Client]):
    def __init__(self, data: ClientSchema) -> None:
        self.data = data

    def _validate(self) -> None:
        pass

    def _start(self) -> ClientSchema:
        with transaction.atomic():
            client, _ = Client.objects.get_or_create(
                full_name=self.data.full_name,
                defaults={"address": self.data.address},
            )
            return ClientSchema.model_validate(
                {"full_name": client.full_name, "address": client.address},
            )
