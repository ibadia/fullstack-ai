from rest_framework import serializers
from .models import Receipt


class ReceiptUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()


class ReceiptStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["id", "status", "extracted_data", "total_amount", "error_message", "created_at"]

class ReceiptListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["id", "image", "status", "extracted_data", "total_amount", "created_at"]