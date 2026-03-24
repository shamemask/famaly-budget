from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils.timezone import make_aware

from transactions.models import Client, Product, Transaction


class ClientModelTest(TestCase):
    @patch("transactions.models.Client.objects")
    def test_client_creation(self, mock_client_objects: Client):
        # Создаем мок для объекта клиента
        mock_client = MagicMock()
        mock_client.full_name = "Иванова Анна Сергеевна"
        mock_client.address = "123456, г. Новгород, ул. Солнечная, д. 10, кв. 20"
        mock_client.created_at = datetime(2025, 4, 22, 10, 0)
        mock_client_objects.create.return_value = mock_client

        # Вызываем создание клиента
        client = Client.objects.create(
            full_name="Иванова Анна Сергеевна",
            address="123456, г. Новгород, ул. Солнечная, д. 10, кв. 20",
        )

        # Проверяем, что метод create был вызван с правильными аргументами
        mock_client_objects.create.assert_called_once_with(
            full_name="Иванова Анна Сергеевна",
            address="123456, г. Новгород, ул. Солнечная, д. 10, кв. 20",
        )
        assert client.full_name == "Иванова Анна Сергеевна"
        assert client.address == "123456, г. Новгород, ул. Солнечная, д. 10, кв. 20"
        assert client.created_at


class ProductModelTest(TestCase):
    @patch("transactions.models.Product.objects")
    @patch("transactions.models.Client.objects")
    def test_product_creation(self, mock_client_objects: Client, mock_product_objects: Product):
        # Мок для клиента
        mock_client = MagicMock()
        mock_client_objects.get.return_value = mock_client

        # Мок для продукта
        mock_product = MagicMock()
        mock_product.contract_number = "1234567890"
        mock_product.contract_date = date(2021, 5, 12)
        mock_product.account_number = "Не активирован"
        mock_product.created_at = make_aware(datetime(2025, 4, 22, 10, 0))
        mock_product_objects.create.return_value = mock_product

        # Вызываем создание продукта
        product = Product.objects.create(
            client=mock_client,
            contract_date=date(2021, 5, 12),
            contract_number="1234567890",
            account_number="Не активирован",
        )

        # Проверяем вызовы
        mock_product_objects.create.assert_called_once_with(
            client=mock_client,
            contract_date=date(2021, 5, 12),
            contract_number="1234567890",
            account_number="Не активирован",
        )
        assert product.account_number == "1234567890"
        assert product.account_number == date(2021, 5, 12)
        assert product.created_at


class TransactionModelTest(TestCase):
    @patch("transactions.models.Transaction.objects")
    @patch("transactions.models.Product.objects")
    def test_transaction_creation(
        self,
        mock_product_objects: Product,
        mock_transaction_objects: Transaction,
    ):
        # Мок для продукта
        mock_product = MagicMock()
        mock_product_objects.get.return_value = mock_product

        # Мок для транзакции
        mock_transaction = MagicMock()
        mock_transaction.amount = Decimal("-1500.00")
        mock_transaction.description = "Оплата в ИП Сидоров В.В."
        mock_transaction.card_last_four = "1234"
        mock_transaction.operation_datetime = make_aware(datetime(2025, 4, 15, 14, 30))
        mock_transaction.created_at = make_aware(datetime(2025, 4, 22, 10, 0))
        mock_transaction_objects.create.return_value = mock_transaction

        # Вызываем создание транзакции
        transaction = Transaction.objects.create(
            product=mock_product,
            operation_datetime=make_aware(datetime(2025, 4, 15, 14, 30)),
            description_date=make_aware(datetime(2025, 4, 15, 14, 31)),
            amount=Decimal("-1500.00"),
            description="Оплата в ИП Сидоров В.В.",
            card_last_four="1234",
        )

        # Проверяем вызовы
        mock_transaction_objects.create.assert_called_once_with(
            product=mock_product,
            operation_datetime=make_aware(datetime(2025, 4, 15, 14, 30)),
            description_date=make_aware(datetime(2025, 4, 15, 14, 31)),
            amount=Decimal("-1500.00"),
            description="Оплата в ИП Сидоров В.В.",
            card_last_four="1234",
        )
        assert transaction.amount == Decimal("-1500.00")
        assert transaction.description == "Оплата в ИП Сидоров В.В."
        assert transaction.card_last_four == "1234"
        assert transaction.created_at
