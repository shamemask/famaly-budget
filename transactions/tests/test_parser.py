from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils.timezone import make_aware


class ParserTest(TestCase):
    def setUp(self):
        self.sample_content = """
Артамонова Мария Леонидовна
Аррес места жительства: 350028, Краснадарский Край, Г Краснодар, Ул Им. 40-летия Победы, д. 101, кв. 109
Дата занлючения договора: 16.08.2020
Номер договора: 0503752719
Номер дицевого счета: Не открывался
| 31.03.2025 18:48 | 31.03.2025 18:49 | -1245.00 P | -1245.00 P | Оплата в ИП Карапетян А.А. | 4838 |
| 31.03.2025 18:43 | 31.03.2025 18:44 | -577.42 P | -577.42 P | Оплата в MAGNIT MM SMURVI_P_QR | 4838 |
        """

    @patch("transactions.models.Client.objects")
    @patch("transactions.models.Product.objects")
    @patch("transactions.models.Transaction.objects")
    def test_parse_client(
        self,
        mock_transaction_objects,
        mock_product_objects,
        mock_client_objects,
    ):
        mock_client = MagicMock()
        mock_client.full_name = "Артамонова Мария Леонидовна"
        mock_client.address = (
            "350028, Краснадарский Край, Г Краснодар, Ул Им. 40-летия Победы, д. 101, кв. 109"
        )
        mock_client_objects.get_or_create.return_value = (mock_client, True)

        mock_product = MagicMock()
        mock_product_objects.get_or_create.return_value = (mock_product, True)

        from monetary_parser.strategems.parser import parse_transaction_data

        parse_transaction_data(self.sample_content)

        mock_client_objects.get_or_create.assert_called_once_with(
            full_name="Артамонова Мария Леонидовна",
            address="350028, Краснадарский Край, Г Краснодар, Ул Им. 40-летия Победы, д. 101, кв. 109",
        )

    @patch("transactions.models.Client.objects")
    @patch("transactions.models.Product.objects")
    @patch("transactions.models.Transaction.objects")
    def test_parse_product(
        self,
        mock_transaction_objects,
        mock_product_objects,
        mock_client_objects,
    ):
        mock_client = MagicMock()
        mock_client_objects.get_or_create.return_value = (mock_client, True)

        mock_product = MagicMock()
        mock_product.contract_number = "0503752719"
        mock_product.contract_date = datetime(2020, 8, 16).date()
        mock_product.account_number = "Не открывался"
        mock_product_objects.get_or_create.return_value = (mock_product, True)

        from monetary_parser.strategems.parser import parse_transaction_data

        parse_transaction_data(self.sample_content)

        mock_product_objects.get_or_create.assert_called_once_with(
            client=mock_client,
            contract_date=datetime(2020, 8, 16).date(),
            contract_number="0503752719",
            account_number="Не открывался",
        )

    @patch("transactions.models.Client.objects")
    @patch("transactions.models.Product.objects")
    @patch("transactions.models.Transaction.objects")
    def test_parse_transactions(
        self,
        mock_transaction_objects,
        mock_product_objects,
        mock_client_objects,
    ):
        mock_client = MagicMock()
        mock_client_objects.get_or_create.return_value = (mock_client, True)

        mock_product = MagicMock()
        mock_product_objects.get_or_create.return_value = (mock_product, True)

        mock_transaction = MagicMock()
        mock_transaction_objects.create.return_value = mock_transaction

        from monetary_parser.strategems.parser import ParserStrategy

        ParserStrategy(self.sample_content)

        assert mock_transaction_objects.create.call_count == 2
        mock_transaction_objects.create.assert_any_call(
            product=mock_product,
            operation_datetime=make_aware(datetime(2025, 3, 31, 18, 48)),
            description_date=make_aware(datetime(2025, 3, 31, 18, 49)),
            amount=Decimal("-1245.00"),
            description="Оплата в ИП Карапетян А.А.",
            card_last_four="4838",
        )
        mock_transaction_objects.create.assert_any_call(
            product=mock_product,
            operation_datetime=make_aware(datetime(2025, 3, 31, 18, 43)),
            description_date=make_aware(datetime(2025, 3, 31, 18, 44)),
            amount=Decimal("-577.42"),
            description="Оплата в MAGNIT MM SMURVI_P_QR",
            card_last_four="4838",
        )
