from unittest.mock import patch
from django.test import TestCase
from apps.users.models import User
from apps.receipts.models import Receipt
from apps.receipts.tasks import process_receipt_task


class ProcessReceiptTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.receipt = Receipt.objects.create(
            user=self.user,
            image="receipts/test.jpg",
            status=Receipt.Status.PENDING,
        )

    @patch("apps.receipts.tasks.ReceiptService")
    def test_task_calls_service_process_receipt(self, mock_service_class):
        process_receipt_task.run(self.receipt.id)
        mock_service_class.assert_called_once_with(receipt_id=self.receipt.id)
        mock_service_class.return_value.process_receipt.assert_called_once()

    @patch("apps.receipts.tasks.ReceiptService")
    def test_task_retries_on_service_failure(self, mock_service_class):
        mock_service_class.return_value.process_receipt.side_effect = ValueError("gemini failed")

        with self.assertRaises(Exception):
            process_receipt_task.apply(args=[self.receipt.id], throw=True)