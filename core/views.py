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
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, SAFE_METHODS, BasePermission
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


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


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
    permission_classes = [IsAdminOrReadOnly]


def extract_pdf_content(file_bytes):
    toc = []
    content = ""
    # 1. Try PyMuPDF
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        toc = doc.get_toc()
        text_list = []
        char_count = 0
        for page in doc:
            text = page.get_text() or ""
            text_list.append(text)
            char_count += len(text)
            if char_count > 100000:
                break
        content = "".join(text_list)
        doc.close()
    except Exception:
        content = ""

    # 2. Fallback to pypdf if empty
    if not content.strip():
        try:
            import io, pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_list = []
            char_count = 0
            for page in reader.pages:
                text = page.extract_text() or ""
                text_list.append(text)
                char_count += len(text)
                if char_count > 100000:
                    break
            content = "".join(text_list)
        except Exception:
            pass

    return content.strip(), toc


class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = PDFUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['pdffile']
        try:
            file_bytes = uploaded_file.read()
            content, toc = extract_pdf_content(file_bytes)

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


class UploadZIPView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminUser]

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
                        
                        with open(pdf_path, 'rb') as f:
                            fbytes = f.read()

                        content, toc = extract_pdf_content(fbytes)
                        title = os.path.splitext(filename)[0]
                        clean_filename = get_valid_filename(filename)
                        unique_name = f"{uuid.uuid4().hex[:8]}_{clean_filename}"

                        book = Book(
                            title=title,
                            author="Noma'lum",
                            genre="PDF",
                            description=f"{title} kitobining elektron nusxasi.",
                            content=content,
                            toc=toc
                        )
                        book.file.save(unique_name, ContentFile(fbytes), save=True)
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
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']

        books = Book.objects.all().order_by('-id')[:10].values('id', 'title', 'author', 'genre', 'description', 'content')
        books_context = "Kutubxonadagi so'nggi kitoblar:\n"
        
        for b in books:
            content_snippet = b['content'][:500] if b['content'] else ""
            books_context += f"---\nID: {b['id']}\nNomi: {b['title']}\nMuallif: {b['author']}\nQisqacha: {b['description']}\nMatn: {content_snippet}...\n---\n"

        if not client:
            return Response({"reply": f"AI yordamchi tayyor. Kontekstda {len(books)} ta kitob mavjud."}, status=status.HTTP_200_OK)

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