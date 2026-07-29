from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count, Sum
from drf_yasg.utils import swagger_auto_schema
from utils.response.resp import APIResponse
from .models import Receipt
from .serializers import ReceiptUploadSerializer, ReceiptStatusSerializer, ReceiptListSerializer
from .tasks import process_receipt_task
from rest_framework.response import Response


class ReceiptAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Upload a receipt image for background analysis. "
                              "Requires authentication. Returns 202 with the receipt id and pending status. "
                              "Processing runs async via Celery, poll GET /api/receipts/{id}/status/ for the result.",
        request_body=ReceiptUploadSerializer,
        responses={202: ReceiptStatusSerializer}
    )
    def post(self, request):
        serializer = ReceiptUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt = Receipt.objects.create(
            user=request.user,
            image=serializer.validated_data["image"],
            status=Receipt.Status.PENDING,
        )

        process_receipt_task.delay(receipt.id)

        response_serializer = ReceiptStatusSerializer(receipt)
        body = APIResponse.get_response(
            message="Receipt queued for analysis",
            data=response_serializer.data
        )
        return Response(body, status=status.HTTP_202_ACCEPTED)
    
class ReceiptListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptListSerializer

    @swagger_auto_schema(
        operation_description="List the authenticated user's receipts, paginated. "
                              "Requires authentication. Only returns receipts owned by the caller.",
        responses={200: ReceiptListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user).order_by("-created_at")


class ReceiptSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get aggregate totals (count and sum) of the authenticated user's receipts. "
                              "Requires authentication. Only counts receipts owned by the caller.",
    )
    def get(self, request):
        result = Receipt.objects.filter(user=request.user).aggregate(
            total_count=Count("id"),
            total_sum=Sum("total_amount"),
        )
        body = APIResponse.get_response(
            message="Summary fetched successfully",
            data={
                "total_count": result["total_count"] or 0,
                "total_sum": result["total_sum"] or 0,
            }
        )
        return Response(body, status=status.HTTP_200_OK)


class ReceiptStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the current status and result of a receipt analysis job. "
                              "Requires authentication. Only returns receipts owned by the caller.",
        responses={200: ReceiptStatusSerializer}
    )
    def get(self, request, receipt_id):
        receipt = Receipt.objects.filter(id=receipt_id, user=request.user).first()
        if not receipt:
            body = APIResponse.get_response(
                message="Receipt not found",
                code=1,
                data={"detail": "Receipt not found"}
            )
            return Response(body, status=status.HTTP_404_NOT_FOUND)

        serializer = ReceiptStatusSerializer(receipt)
        body = APIResponse.get_response(
            message="Receipt status fetched successfully",
            data=serializer.data
        )
        return Response(body, status=status.HTTP_200_OK)