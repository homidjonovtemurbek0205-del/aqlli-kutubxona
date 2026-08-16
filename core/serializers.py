from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Book, User

User = get_user_model()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

class BookSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'description', 'content', 'file', 'toc', 'created_at']

    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file and request is not None:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

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