"""Serializers for receipt API."""

from rest_framework import serializers

from apps.receipts.models import Receipt, ReceiptLineItem


class ReceiptLineItemSerializer(serializers.ModelSerializer):
    """Serializer for receipt line items."""

    class Meta:
        model = ReceiptLineItem
        fields = [
            "id",
            "description",
            "quantity",
            "unit_price",
            "total_price",
            "category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for receipts."""

    line_items = ReceiptLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = [
            "id",
            "file",
            "file_name",
            "analysis_status",
            "analysis_provider",
            "analysis_model",
            "extracted_data",
            "line_items",
            "error_message",
            "error_code",
            "processing_time_ms",
            "file_size_bytes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "analysis_status",
            "analysis_provider",
            "analysis_model",
            "extracted_data",
            "line_items",
            "error_message",
            "error_code",
            "processing_time_ms",
            "file_size_bytes",
            "created_at",
            "updated_at",
        ]


class ReceiptUploadSerializer(serializers.Serializer):
    """Serializer for receipt file upload."""

    file = serializers.ImageField(required=True)

    def validate_file(self, value):
        """Validate file size and type."""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB")

        # Check file type
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"File type must be one of: {', '.join(allowed_types)}"
            )

        return value