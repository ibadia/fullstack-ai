from django.test.utils import CaptureQueriesContext
from django.db import connection
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.receipts.models import Receipt


class ReceiptListViewQueryCountTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user1@example.com")
        self.client.force_authenticate(user=self.user)
        for i in range(5):
            Receipt.objects.create(user=self.user, image=f"receipts/{i}.jpg", status=Receipt.Status.DONE)

    def test_list_query_count_does_not_grow_with_receipt_count(self):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get("/api/receipts/")
        query_count_5 = len(ctx.captured_queries)

        for i in range(5, 15):
            Receipt.objects.create(user=self.user, image=f"receipts/{i}.jpg", status=Receipt.Status.DONE)

        with CaptureQueriesContext(connection) as ctx:
            self.client.get("/api/receipts/")
        query_count_15 = len(ctx.captured_queries)

        self.assertEqual(query_count_5, query_count_15)