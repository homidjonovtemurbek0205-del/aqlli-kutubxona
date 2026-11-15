<<<<<<< HEAD
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Book, User

User = get_user_model()

<<<<<<< HEAD

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD


=======
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

>>>>>>> abd65b8 (yana)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_staff', 'is_superuser']

<<<<<<< HEAD

=======
>>>>>>> abd65b8 (yana)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        extra_kwargs = {'username': {'required': False}}

    def create(self, validated_data):
<<<<<<< HEAD
        username = validated_data.get('username') or validated_data['email'].split('@', 1)[0]
        user = User.objects.create_user(
            email=validated_data['email'],
            username=username,
            password=validated_data['password'],
        )
        return user


=======
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),
            password=validated_data['password']
        )
        return user

>>>>>>> abd65b8 (yana)
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

<<<<<<< HEAD

=======
>>>>>>> abd65b8 (yana)
class PDFUploadSerializer(serializers.Serializer):
    pdffile = serializers.FileField(required=True)

    def validate_pdffile(self, value):
        if not value.name.lower().endswith('.pdf'):
<<<<<<< HEAD
            raise serializers.ValidationError('Faqat .pdf formatidagi fayllarni yuklashingiz mumkin.')
        return value


=======
            raise serializers.ValidationError("Faqat .pdf formatidagi fayllarni yuklashingiz mumkin.")
        return value

>>>>>>> abd65b8 (yana)
class ZIPUploadSerializer(serializers.Serializer):
    zipfile = serializers.FileField(required=True)

    def validate_zipfile(self, value):
        if not value.name.lower().endswith('.zip'):
<<<<<<< HEAD
            raise serializers.ValidationError('Faqat .zip formatidagi fayllarni yuklashingiz mumkin.')
        return value


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
=======
            raise serializers.ValidationError("Faqat .zip formatidagi fayllarni yuklashingiz mumkin.")
        return value

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
>>>>>>> abd65b8 (yana)
=======
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Book, User

User = get_user_model()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_staff', 'is_superuser']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        extra_kwargs = {'username': {'required': False}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),
            password=validated_data['password']
        )
        return user

class BookSerializer(serializers.ModelSerializer):
    has_audio = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'genre', 'description', 
            'content', 'file', 'audio_file', 'audiobook_url', 
            'has_audio', 'toc', 'created_at'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if instance.file:
            ret['file'] = request.build_absolute_uri(instance.file.url) if request else instance.file.url
        if instance.audio_file:
            ret['audio_file'] = request.build_absolute_uri(instance.audio_file.url) if request else instance.audio_file.url
        elif instance.audiobook_url:
            ret['audio_file'] = instance.audiobook_url
        return ret

class PDFUploadSerializer(serializers.Serializer):
    pdffile = serializers.FileField(required=True)

    def validate_pdffile(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Faqat .pdf formatidagi fayllarni yuklashingiz mumkin.")
        return value

class AudioUploadSerializer(serializers.Serializer):
    audio_file = serializers.FileField(required=False)
    audiobook_url = serializers.URLField(required=False, allow_blank=True)

    def validate(self, attrs):
        audio_file = attrs.get('audio_file')
        audiobook_url = attrs.get('audiobook_url')
        if not audio_file and not audiobook_url:
            raise serializers.ValidationError("Audio fayl yoki audio havola kiritilishi kerak.")
        if audio_file:
            valid_exts = ('.mp3', '.wav', '.m4a', '.ogg', '.aac', '.flac', '.opus')
            if not any(audio_file.name.lower().endswith(ext) for ext in valid_exts):
                raise serializers.ValidationError("Faqat audio formatdagi (.mp3, .wav, .m4a, .ogg, .aac) fayllarni yuklashingiz mumkin.")
        return attrs

class ZIPUploadSerializer(serializers.Serializer):
    zipfile = serializers.FileField(required=True)

    def validate_zipfile(self, value):
        if not value.name.lower().endswith('.zip'):
            raise serializers.ValidationError("Faqat .zip formatidagi fayllarni yuklashingiz mumkin.")
        return value

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
>>>>>>> 5cc9508 (O'zgarishlar saqlandi)
