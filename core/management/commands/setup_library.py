import os
import re
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from core.models import Book
from core.views import extract_pdf_content

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds default users and indexes existing books from media/books/ into the database."

    def handle(self, *args, **options):
        self.stdout.write("1. Setting up default users...")
        # 1. Admin user
        admin_user, created = User.objects.get_or_create(
            email="admin@library.com",
            defaults={"username": "admin", "is_staff": True, "is_superuser": True}
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(" - Created admin user: admin@library.com / admin123"))
        else:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(" - Admin user ready: admin@library.com / admin123")

        # 2. Regular user
        regular_user, created = User.objects.get_or_create(
            email="user@library.com",
            defaults={"username": "kitobxon"}
        )
        if created:
            regular_user.set_password("user123")
            regular_user.save()
            self.stdout.write(self.style.SUCCESS(" - Created user: user@library.com / user123"))
        else:
            self.stdout.write(" - User ready: user@library.com / user123")

        # 3. Scan and index books in media/books/
        books_dir = os.path.join(settings.MEDIA_ROOT, 'books')
        if not os.path.exists(books_dir):
            self.stdout.write(self.style.WARNING(" - media/books directory does not exist."))
            return

        self.stdout.write("\n2. Scanning media/books/ for PDF books...")
        files = os.listdir(books_dir)
        added_count = 0
        updated_count = 0

        # Sample free audio streams for well-known books to have instant rich audio experience
        sample_audio_map = {
            "o'tkan kunlar": "https://ia800301.us.archive.org/15/items/otkan-kunlar/otkan_kunlar_01.mp3",
            "alkimyogar": "https://ia801503.us.archive.org/15/items/alkimyogar/alkimyogar_01.mp3",
            "garri potter": "https://ia802808.us.archive.org/32/items/harrypotterandsorcerersstone_202004/Chapter%2001.mp3",
            "atom odatlar": "https://ia600905.us.archive.org/19/items/audiobook_sample/sample.mp3",
            "boy ota": "https://ia600905.us.archive.org/19/items/audiobook_sample/sample.mp3",
        }

        for filename in files:
            if not filename.lower().endswith('.pdf'):
                continue

            rel_path = f"books/{filename}"
            full_path = os.path.join(books_dir, filename)

            # Clean raw filename to human readable title and author
            base_name = os.path.splitext(filename)[0]
            cleaned = re.sub(r'^[0-9a-fA-F]{8}_', '', base_name)
            cleaned_title = cleaned.replace('_', ' ').replace('-', ' ').strip()

            author = "Noma'lum"
            genre = "Badiiy"

            lower_cleaned = cleaned_title.lower()
            if "garri potter" in lower_cleaned or "harry potter" in lower_cleaned:
                author = "J.K. Rowling"
                genre = "Fantastika"
            elif "atom odatlar" in lower_cleaned:
                author = "James Clear"
                genre = "Psixologiya & Rivojlanish"
            elif "boy ota" in lower_cleaned:
                author = "Robert Kiyosaki"
                genre = "Biznes & Moliya"
            elif "inson psixologiyasi" in lower_cleaned or "psixologiya" in lower_cleaned:
                author = "Psixologiya Markazi"
                genre = "Psixologiya"
            elif "qodiriy" in lower_cleaned or "o'tkan kunlar" in lower_cleaned or "otkan kunlar" in lower_cleaned:
                author = "Abdulla Qodiriy"
                genre = "Tarixiy Roman"
            elif "alkimyogar" in lower_cleaned:
                author = "Paulo Koelyo"
                genre = "Falsafiy & Motivatsiya"
            elif "xamsa" in lower_cleaned or "navoiy" in lower_cleaned:
                author = "Alisher Navoiy"
                genre = "Mumtoz Adabiyot"
            elif "gazzoliy" in lower_cleaned or "alloh" in lower_cleaned or "qalb" in lower_cleaned or "duo" in lower_cleaned:
                author = "Diniy-ma'rifiy"
                genre = "Ma'rifat & Tarbiya"

            book = Book.objects.filter(file=rel_path).first()
            if not book:
                book = Book.objects.filter(title__iexact=cleaned_title).first()

            audio_url = None
            for key, aurl in sample_audio_map.items():
                if key in lower_cleaned:
                    audio_url = aurl
                    break

            if not book:
                content = ""
                toc = []
                try:
                    with open(full_path, 'rb') as f:
                        fbytes = f.read()
                    content, toc = extract_pdf_content(fbytes)
                except Exception:
                    content = f"{cleaned_title} kitobi."

                desc = f"{cleaned_title} - {author} qalamiga mansub sara asar."
                if content and len(content) > 100:
                    desc = content[:250].strip() + "..."

                book = Book.objects.create(
                    title=cleaned_title,
                    author=author,
                    genre=genre,
                    description=desc,
                    content=content,
                    file=rel_path,
                    audiobook_url=audio_url,
                    toc=toc
                )
                added_count += 1
            else:
                if audio_url and not book.audiobook_url and not book.audio_file:
                    book.audiobook_url = audio_url
                    book.save()
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done! Added {added_count} new books, updated {updated_count} books. Total books in DB: {Book.objects.count()}"
        ))
