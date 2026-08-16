import os
import uuid
import shutil
import zipfile
import pymupdf
from google import genai

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Book
from .serializers import (
    BookSerializer, 
    PDFUploadSerializer, 
    ZIPUploadSerializer, 
    ChatRequestSerializer
)

# Gemini API sozlamasi
gemini_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=gemini_key) if gemini_key else None


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = PDFUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['pdffile']
        
        # PyMuPDF xotiradagi (memory) fayldan to'g'ridan-to'g'ri o'qiy oladi!
        # Diskka vaqtinchalik saqlash shart emas.
        doc = None
        try:
            file_bytes = uploaded_file.read()
            doc = fitz.open(stream=file_bytes, filetype="pdf")
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
            
            # Faylni Django storage orqali saqlash
            unique_name = f"{uuid.uuid4()}.pdf"
            
            book = Book(
                title=title,
                author="Noma'lum",
                genre="PDF",
                description=f"{title} kitobining elektron nusxasi.",
                content=content,
                toc=toc
            )
            book.file.save(unique_name, ContentFile(file_bytes), save=True)

            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"PDF faylni o'qishda xatolik: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if doc:
                doc.close()


class UploadZIPView(APIView):
    parser_classes = (MultiPartParser, FormParser)

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
                # Zip Slip xavfsizlik tekshiruvi
                for member in zip_ref.infolist():
                    member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                    if not member_path.startswith(os.path.abspath(temp_dir)):
                        raise Exception("Arxiv ichida xavfsiz bo'lmagan fayl yo'li aniqlandi (Zip Slip).")
                zip_ref.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, filename)
                        
                        doc = None
                        try:
                            doc = fitz.open(pdf_path)
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
                        unique_name = f"{uuid.uuid4()}.pdf"

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
                "message": f"{len(added_books)} ta PDF kitob muvaffaqiyatli qo'shildi.",
                "books": BookSerializer(added_books, many=True).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"ZIP arxivni qayta ishlashda xatolik: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


class AIChatView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request, *args, **kwargs):
        if not client:
            return Response({"reply": "Xatolik: Gemini API kaliti sozlanmagan."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']

        books = Book.objects.all().order_by('-id')[:10].values('id', 'title', 'author', 'genre', 'description', 'content')
        books_context = "Kutubxonadagi so'nggi kitoblar ro'yxati:\n"
        
        for b in books:
            content_snippet = b['content'][:500] if b['content'] else ""
            books_context += f"""---
ID: {b['id']}
Nomi: {b['title']}
Muallif: {b['author']}
Janri: {b['genre']}
Qisqacha tavsif: {b['description']}
Matndan parcha: {content_snippet}... 
---\n"""

        system_instruction = """Siz "Aqlli Kutubxona"ning AI yordamchisisiz. Sizning vazifalaringiz:
1. Foydalanuvchi so'ragan janr yoki mavzudagi kitoblarni tavsiya qilish.
2. Foydalanuvchi biror kitob haqida so'rasa, uning mazmunini aytib berish.
3. Foydalanuvchi bilan o'qigan kitoblari bo'yicha savol-javob qilish.
4. Foydalanuvchi kitob qidirsa, unga yordam berish.
Javoblaringizni doim o'zbek tilida, xushmuomila va aniq bering."""

        prompt = f"""MAVJUD KITOBLAR MA'LUMOTI:
{books_context}

Foydalanuvchi savoli: {user_message}"""

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    "system_instruction": system_instruction
                }
            )
            return Response({"reply": response.text}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"reply": f"Google Gemini API bilan bog'lanishda xatolik: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)