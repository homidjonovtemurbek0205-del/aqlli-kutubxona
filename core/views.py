import os
import uuid
import shutil
import zipfile
import pymupdf
from google import genai

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Book, User
from .serializers import (
    BookSerializer, 
    PDFUploadSerializer, 
    ZIPUploadSerializer, 
    ChatRequestSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer
)

gemini_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=gemini_key) if gemini_key else None


def index_view(request):
    return render(request, 'core/index.html')


class EmailTokenObtainView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PDFUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['pdffile']
        doc = None
        try:
            file_bytes = uploaded_file.read()
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            toc = doc.get_toc()

            text_list = []
            char_count = 0
            for page in doc:
                text = page.get_text()
                text_list.append(text)
                char_count += len(text)
                if char_count > 50000:
                    break
            content = "".join(text_list)

            title = os.path.splitext(uploaded_file.name)[0]
            clean_filename = get_valid_filename(uploaded_file.name)
            unique_name = f"{uuid.uuid4().hex[:8]}_{clean_filename}"
            
            book = Book(
                title=title,
                author="Noma'lum",
                genre="PDF",
                description=f"{title} kitobining elektron nusxasi.",
                content=content,
                toc=toc
            )
            book.file.save(unique_name, ContentFile(file_bytes), save=True)

            return Response(BookSerializer(book, context={'request': request}).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"PDF faylni o'qishda xatolik: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if doc:
                doc.close()


class UploadZIPView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ZIPUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['zipfile']
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)

        added_books = []
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                for member in zip_ref.infolist():
                    member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                    if not member_path.startswith(os.path.abspath(temp_dir)):
                        raise Exception("Zip Slip xavfi aniqlandi.")
                zip_ref.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, filename)
                        
                        doc = None
                        try:
                            doc = pymupdf.open(pdf_path)
                            toc = doc.get_toc()

                            text_list = []
                            char_count = 0
                            for page in doc:
                                text = page.get_text()
                                text_list.append(text)
                                char_count += len(text)
                                if char_count > 50000:
                                    break
                            content = "".join(text_list)
                        finally:
                            if doc:
                                doc.close()

                        title = os.path.splitext(filename)[0]
                        clean_filename = get_valid_filename(filename)
                        unique_name = f"{uuid.uuid4().hex[:8]}_{clean_filename}"

                        with open(pdf_path, 'rb') as f:
                            book = Book(
                                title=title,
                                author="Noma'lum",
                                genre="PDF",
                                description=f"{title} kitobining elektron nusxasi.",
                                content=content,
                                toc=toc
                            )
                            book.file.save(unique_name, ContentFile(f.read()), save=True)
                            added_books.append(book)

            return Response({
                "message": f"{len(added_books)} ta PDF kitob qo'shildi.",
                "books": BookSerializer(added_books, many=True, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"ZIP arxivda xatolik: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


class AIChatView(APIView):
    parser_classes = (JSONParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not client:
            return Response({"reply": "Gemini API sozlanmagan."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']

        books = Book.objects.all().order_by('-id')[:10].values('id', 'title', 'author', 'genre', 'description', 'content')
        books_context = "Kutubxonadagi so'nggi kitoblar:\n"
        
        for b in books:
            content_snippet = b['content'][:500] if b['content'] else ""
            books_context += f"---\nID: {b['id']}\nNomi: {b['title']}\nMuallif: {b['author']}\nQisqacha: {b['description']}\nMatn: {content_snippet}...\n---\n"

        prompt = f"KUTUBXONA MA'LUMOTLARI:\n{books_context}\n\nFoydalanuvchi: {user_message}"

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={"system_instruction": "Siz Aqlli Kutubxonaning AI yordamchisisiz. Foydalanuvchiga kitoblar bo'yicha yordam bering."}
            )
            return Response({"reply": response.text}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"reply": f"AI Xatolik: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)