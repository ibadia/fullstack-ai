from django.urls import path
from .views import ReceiptAnalyzeView, ReceiptListView, ReceiptSummaryView, ReceiptStatusView

urlpatterns = [
    path("analyze/", ReceiptAnalyzeView.as_view(), name="receipt-analyze"),
    path("", ReceiptListView.as_view(), name="receipt-list"),
    path("summary/", ReceiptSummaryView.as_view(), name="receipt-summary"),
    path("<int:receipt_id>/status/", ReceiptStatusView.as_view(), name="receipt-status"),
]