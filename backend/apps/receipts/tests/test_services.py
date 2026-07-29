from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from apps.users.models import User
from apps.receipts.models import Receipt
from apps.receipts.services import ReceiptService


class ReceiptServiceProcessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.receipt = Receipt.objects.create(
            user=self.user,
            image="receipts/test.jpg",
            status=Receipt.Status.PENDING,
        )

    @patch("apps.receipts.services.genai.Client")
    def test_process_receipt_saves_extracted_data_and_marks_done(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.text = '{"total_amount": 16.5, "merchant_name": "SHOP"}'
        mock_client_class.return_value.models.generate_content.return_value = mock_response

        with patch.object(Receipt.image.field, "storage") as mock_storage:
            mock_storage.open.return_value.read.return_value = b"fake image bytes"
            service = ReceiptService(receipt_id=self.receipt.id)
            result = service.process_receipt()

        self.assertEqual(result.status, Receipt.Status.DONE)
        self.assertEqual(result.total_amount, Decimal("16.5"))
        self.assertEqual(result.extracted_data["merchant_name"], "SHOP")

    @patch("apps.receipts.services.genai.Client")
    def test_process_receipt_marks_failed_on_invalid_json(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.text = "not valid json at all"
        mock_client_class.return_value.models.generate_content.return_value = mock_response

        with patch.object(Receipt.image.field, "storage") as mock_storage:
            mock_storage.open.return_value.read.return_value = b"fake image bytes"
            service = ReceiptService(receipt_id=self.receipt.id)
            with self.assertRaises(ValueError):
                service.process_receipt()

        self.receipt.refresh_from_db()
        self.assertEqual(self.receipt.status, Receipt.Status.FAILED)
        self.assertIsNotNone(self.receipt.error_message)

    @patch("apps.receipts.services.genai.Client")
    def test_process_receipt_marks_failed_when_total_amount_missing(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.text = '{"merchant_name": "SHOP"}'
        mock_client_class.return_value.models.generate_content.return_value = mock_response

        with patch.object(Receipt.image.field, "storage") as mock_storage:
            mock_storage.open.return_value.read.return_value = b"fake image bytes"
            service = ReceiptService(receipt_id=self.receipt.id)
            with self.assertRaises(ValueError):
                service.process_receipt()

        self.receipt.refresh_from_db()
        self.assertEqual(self.receipt.status, Receipt.Status.FAILED)

    def test_parse_json_handles_markdown_code_fence(self):
        service = ReceiptService(receipt_id=self.receipt.id)
        raw = '```json\n{"total_amount": 5}\n```'
        result = service._parse_json(raw)
        self.assertEqual(result["total_amount"], 5)

    def test_extract_total_converts_to_decimal(self):
        service = ReceiptService(receipt_id=self.receipt.id)
        result = service._extract_total({"total_amount": 12.34})
        self.assertEqual(result, Decimal("12.34"))
    def test_parse_json_raises_when_braces_found_but_content_invalid(self):
        service = ReceiptService(receipt_id=self.receipt.id)
        raw = '{"total_amount": 16.5, invalid content here}'
        with self.assertRaises(ValueError):
            service._parse_json(raw)