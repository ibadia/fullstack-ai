from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.receipts.models import Receipt


class ReceiptListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user1@example.com")
        self.other_user = User.objects.create(email="user2@example.com")
        self.client.force_authenticate(user=self.user)

        Receipt.objects.create(user=self.user, image="receipts/a.jpg", status=Receipt.Status.DONE)
        Receipt.objects.create(user=self.other_user, image="receipts/b.jpg", status=Receipt.Status.DONE)

    def test_list_only_returns_receipts_owned_by_authenticated_user(self):
        response = self.client.get("/api/receipts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]
        self.assertEqual(len(results), 1)


class ReceiptSummaryViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user1@example.com")
        self.other_user = User.objects.create(email="user2@example.com")
        self.client.force_authenticate(user=self.user)

        Receipt.objects.create(user=self.user, total_amount=10, image="receipts/a.jpg", status=Receipt.Status.DONE)
        Receipt.objects.create(user=self.user, total_amount=20, image="receipts/b.jpg", status=Receipt.Status.DONE)
        Receipt.objects.create(user=self.other_user, total_amount=999, image="receipts/c.jpg", status=Receipt.Status.DONE)

    def test_summary_only_aggregates_authenticated_users_receipts(self):
        response = self.client.get("/api/receipts/summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total_count"], 2)
        self.assertEqual(float(response.data["data"]["total_sum"]), 30.0)


class ReceiptStatusViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user1@example.com")
        self.other_user = User.objects.create(email="user2@example.com")
        self.client.force_authenticate(user=self.user)
        self.receipt = Receipt.objects.create(user=self.user, image="receipts/a.jpg", status=Receipt.Status.DONE)
        self.other_receipt = Receipt.objects.create(user=self.other_user, image="receipts/b.jpg", status=Receipt.Status.DONE)

    def test_status_returns_200_for_own_receipt(self):
        response = self.client.get(f"/api/receipts/{self.receipt.id}/status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["id"], self.receipt.id)

    def test_status_returns_404_for_other_users_receipt(self):
        response = self.client.get(f"/api/receipts/{self.other_receipt.id}/status/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)