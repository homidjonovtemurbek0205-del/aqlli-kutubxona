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

from rest_framework.decorators import action
from django.db.models import Q

from .models import Book, User
from .serializers import (
    BookSerializer, 
    PDFUploadSerializer, 
    ZIPUploadSerializer, 
    ChatRequestSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    AudioUploadSerializer
)

gemini_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=gemini_key) if gemini_key else None


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


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
    queryset = Book.objects.all().order_by('-id')
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], parser_classes=[MultiPartParser, FormParser])
    def upload_audio(self, request, pk=None):
        book = self.get_object()
        serializer = AudioUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if 'audio_file' in serializer.validated_data:
            audio_file = serializer.validated_data['audio_file']
            clean_filename = get_valid_filename(audio_file.name)
            unique_name = f"{uuid.uuid4().hex[:8]}_{clean_filename}"
            book.audio_file.save(unique_name, audio_file, save=False)
        
        if 'audiobook_url' in serializer.validated_data:
            book.audiobook_url = serializer.validated_data['audiobook_url']
        
        book.save()
        return Response(BookSerializer(book, context={'request': request}).data, status=status.HTTP_200_OK)



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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message'].strip()
        lower_msg = user_message.lower()

        # 1. Gather comprehensive library knowledge base statistics
        total_books = Book.objects.count()
        audio_books_count = Book.objects.filter(
            Q(audio_file__isnull=False) & ~Q(audio_file='') |
            Q(audiobook_url__isnull=False) & ~Q(audiobook_url='')
        ).count()
        genres = [g for g in Book.objects.exclude(genre__isnull=True).exclude(genre='').values_list('genre', flat=True).distinct() if g]
        authors = [a for a in Book.objects.exclude(author__isnull=True).exclude(author='').values_list('author', flat=True).distinct() if a]

        # 2. Build catalog overview
        all_books = Book.objects.all().order_by('-id')
        catalog_summary = []
        for b in all_books[:100]:
            has_audio_str = "Audio kitob mavjud" if b.has_audio else "Faqat matn/PDF"
            catalog_summary.append(f"• ID: {b.id} | \"{b.title}\" | Muallif: {b.author} | Janr: {b.genre} | {has_audio_str}")

        catalog_text = "\n".join(catalog_summary)

        # 3. Targeted book content retrieval (RAG)
        matched_books = []
        for word in user_message.split():
            clean_word = "".join(c for c in word if c.isalnum() or c in ("'", "‘", "ʻ"))
            if len(clean_word) >= 3 and clean_word.lower() not in {"kitob", "haqida", "qanaqa", "qanday", "nima", "kim", "bor", "bormi", "aytib", "ber"}:
                q_books = Book.objects.filter(
                    Q(title__icontains=clean_word) | 
                    Q(author__icontains=clean_word) | 
                    Q(description__icontains=clean_word)
                )[:3]
                for mb in q_books:
                    if mb not in matched_books:
                        matched_books.append(mb)
            if len(matched_books) >= 4:
                break

        matched_details = ""
        if matched_books:
            matched_details = "\n\nSO'ROV BO'YICHA TOPILGAN KITOBLARNING TO'LIQROQ MATNI VA TAVSIFI:\n"
            for mb in matched_books:
                content_excerpt = (mb.content or '')[:2000].strip()
                matched_details += f"---\nKitob: \"{mb.title}\" (Muallif: {mb.author})\nJanr: {mb.genre}\nTavsif: {mb.description or 'Tavsif mavjud emas'}\nAsar matnidan parcha:\n{content_excerpt}\n---\n"

        prompt = f"""KUTUBXONA MA'LUMOTLARI VA STATISTIKASI:
- Jami kitoblar soni: {total_books} ta
- Audio kitoblar soni: {audio_books_count} ta
- Mavjud janrlar ({len(genres)} ta): {', '.join(genres)}
- Asosiy mualliflar ({len(authors)} ta): {', '.join(authors[:30])}

BARCHA KITOBLAR RO'YXATI:
{catalog_text}
{matched_details}

FOYDALANUVCHI SAVOLI: {user_message}"""

        system_instruction = (
            "Siz 'Aqlli Kutubxona' (Smart Library) tizimining intellektual, muloyim va har tomonlama bilimdon AI kutubxonachisisiz.\n"
            "Vazifalaringiz:\n"
            "1. Foydalanuvchining kitoblar bo'yicha har qanday savoliga (syujet, qahramonlar, mualliflar, mavzular, tavsiflar) aniq javob bering.\n"
            "2. Miqdoriy savollarga (masalan: 'Kutubxonada nechta kitob bor?', '[Muallif]ning nechta kitobi bor?', 'Qaysi audio kitoblar bor?') yuqoridagi statistikaga tayanib 100% aniq raqamlar bilan javob bering.\n"
            "3. Agar kitobda audio mavjud bo'lsa, uni saytda to'g'ridan-to'g'ri tinglash mumkinligini eslatib o'ting.\n"
            "4. Doimo samimiy, o'zbek tilida (yoki foydalanuvchi so'ragan tilda) va o'qishga qulay chiroyli formatda javob bering."
        )

        def local_fallback_answer():
            if any(q in lower_msg for q in ["nechta kitob", "kitoblar soni", "kitob soni", "how many books"]):
                return f"Hozirda kutubxonamiz fondida jami **{total_books} ta** kitob mavjud. Shulardan **{audio_books_count} tasida** audio kitob nusxasi ham tinglash uchun tayyor!"
            if any(q in lower_msg for q in ["audio kitob", "audiobook", "tinglash"]):
                audio_list = [b.title for b in Book.objects.all() if b.has_audio][:10]
                if audio_list:
                    titles_str = ", ".join(f'"{t}"' for t in audio_list)
                    return f"Kutubxonamizda jami **{audio_books_count} ta** audio kitob mavjud. Masalan: {titles_str}."
                return f"Hozirda kutubxonamizda {audio_books_count} ta audio kitob mavjud."
            if any(q in lower_msg for q in ["janr", "genre", "qanday janr"]):
                return f"Kutubxonamizdagi asosiy janrlar: **{', '.join(genres)}**."
            if any(q in lower_msg for q in ["muallif", "yozuvchi", "author"]):
                return f"Kutubxonamizdagi mashhur mualliflar: {', '.join(authors[:12])}."
            if matched_books:
                b = matched_books[0]
                has_a = "Audiokorpus mavjud va uni to'g'ridan-to'g'ri tinglashingiz mumkin." if b.has_audio else "Ushbu kitobni elektron o'qishingiz mumkin."
                return f"**{b.title}** (Muallif: {b.author}, Janr: {b.genre})\n\n{b.description or ''}\n\n{has_a}"
            return f"Salom! Men 'Aqlli Kutubxona'ning AI yordamchisiman. Kutubxonamizda {total_books} ta kitob va {audio_books_count} ta audio kitob mavjud. Istalgan kitob, muallif yoki janr haqida so'rashingiz mumkin!"

        if not client:
            return Response({"reply": local_fallback_answer()}, status=status.HTTP_200_OK)

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={"system_instruction": system_instruction}
            )
            return Response({"reply": response.text}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"reply": local_fallback_answer()}, status=status.HTTP_200_OK)
