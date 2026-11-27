from datetime import date
from decimal import Decimal
import io
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Item, Receipt


class ReceiptModelTest(TestCase):
    def setUp(self):
        self.receipt = Receipt.objects.create(
            store_name='Maxima',
            date=date(2026, 11, 20),
            total_amount=Decimal('10.00'),
            file_hash='a' * 64,
        )
        self.item = Item.objects.create(
            receipt=self.receipt,
            name='Pienas',
            price=Decimal('10.00'),
            quantity=2,
            category=Item.Category.DRINKS,
        )

    def test_create_receipt_and_items(self):
        self.assertEqual(self.receipt.items.count(), 1)
        self.assertEqual(self.item.receipt, self.receipt)
        self.assertIn('Maxima', str(self.receipt))

    def test_delete_receipt_cascades_to_items(self):
        self.receipt.delete()

        self.assertEqual(Receipt.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)


class ReceiptUploadViewTest(TestCase):
    @patch('receipts.views.ai.extract_receipt')
    def test_upload_receipt_success_creates_receipt_and_items(self, mock_extract):
        mock_extract.return_value = {
            'store_name': 'Maxima',
            'date': '2026-11-20',
            'total_amount': '2.50',
            'items': [
                {
                    'name': 'Pienas',
                    'price': '2.50',
                    'quantity': 1,
                    'category': 'drinks',
                }
            ],
        }

        buffer = io.BytesIO()
        img = Image.new('RGB', (1, 1), color='red')
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        image = SimpleUploadedFile('receipt.jpg', buffer.read(), content_type='image/jpeg')
        url = reverse('upload')

        response = self.client.post(url, {'image': image})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Receipt.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 1)

        receipt = Receipt.objects.get()
        self.assertEqual(receipt.store_name, 'Maxima')
        self.assertEqual(receipt.total_amount, Decimal('2.50'))
        mock_extract.assert_called_once()