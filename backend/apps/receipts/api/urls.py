from django.urls import path

from apps.receipts.api.views import (
    ReceiptUploadAPIView,
    ReceiptDetailAPIView,
    ReceiptListAPIView,
    ReceiptLineItemsAPIView,
)

urlpatterns = [
    path("upload/", ReceiptUploadAPIView.as_view(), name="receipt-upload"),
    path("", ReceiptListAPIView.as_view(), name="receipt-list"),
    path("<int:receipt_id>/", ReceiptDetailAPIView.as_view(), name="receipt-detail"),
    path("<int:receipt_id>/line-items/", ReceiptLineItemsAPIView.as_view(), name="receipt-line-items"),
]