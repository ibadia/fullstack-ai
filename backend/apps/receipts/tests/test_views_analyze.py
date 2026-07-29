from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.users.models import User
from apps.receipts.models import Receipt


class ReceiptAnalyzeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.client.force_authenticate(user=self.user)
        self.url = "/api/receipts/analyze/"

    def _get_test_image(self):
        content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        )
        return SimpleUploadedFile("receipt.gif", content, content_type="image/gif")

    def test_unauthenticated_request_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {"image": self._get_test_image()}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_image_returns_400(self):
        response = self.client.post(self.url, {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.receipts.views.process_receipt_task")
    def test_valid_upload_returns_202_with_pending_status(self, mock_task):
        response = self.client.post(self.url, {"image": self._get_test_image()}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["data"]["status"], "pending")
        mock_task.delay.assert_called_once()

    @patch("apps.receipts.views.process_receipt_task")
    def test_valid_upload_creates_receipt_owned_by_user(self, mock_task):
        response = self.client.post(self.url, {"image": self._get_test_image()}, format="multipart")

        receipt_id = response.data["data"]["id"]
        receipt = Receipt.objects.get(id=receipt_id)
        self.assertEqual(receipt.user, self.user)