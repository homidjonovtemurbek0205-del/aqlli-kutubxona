from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 
            'title', 
            'author', 
            'genre', 
            'description', 
            'content', 
            'file', 
            'toc', 
            'created_at'
        ]

class PDFUploadSerializer(serializers.Serializer):
    pdffile = serializers.FileField(required=True)

    def validate_pdffile(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Faqat .pdf formatidagi fayllarni yuklashingiz mumkin.")
        return value

class ZIPUploadSerializer(serializers.Serializer):
    zipfile = serializers.FileField(required=True)

    def validate_zipfile(self, value):
        if not value.name.lower().endswith('.zip'):
            raise serializers.ValidationError("Faqat .zip formatidagi fayllarni yuklashingiz mumkin.")
        return value

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)