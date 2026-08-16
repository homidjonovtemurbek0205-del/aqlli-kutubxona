import os
import io
import zipfile
import pymupdf

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Book
from core.views import extract_pdf_content

User = get_user_model()


def create_sample_pdf_bytes(text="Aqlli Kutubxona PDF Test Matni"):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class PDFExtractionAndLibraryTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email='admin@library.com',
            password='adminpassword123',
            username='adminuser'
        )
        self.regular_user = User.objects.create_user(
            email='user@library.com',
            password='userpassword123',
            username='regularuser'
        )

    def test_pdf_text_extraction(self):
        """PDF fayldan matn to'g'ri o'qib olinishini tekshirish"""
        sample_text = "O'zbekiston Milliy Kutubxonasi Elektron Nusxa"
        pdf_bytes = create_sample_pdf_bytes(sample_text)
        
        extracted_text, toc = extract_pdf_content(pdf_bytes)
        self.assertIn(sample_text, extracted_text)

    def test_admin_upload_pdf_and_context(self):
        """Admin tarafidan PDF yuklanganda baza va faylda saqlanishini hamda text extract bo'lishini tekshirish"""
        self.client.force_authenticate(user=self.admin)
        
        sample_text = "Alisher Navoiy Xamsa asari matni"
        pdf_bytes = create_sample_pdf_bytes(sample_text)
        pdf_file = SimpleUploadedFile("xamsa.pdf", pdf_bytes, content_type="application/pdf")

        response = self.client.post('/api/upload-pdf/', {'pdffile': pdf_file}, format='multipart')
        self.assertEqual(response.status_code, 201)

        book = Book.objects.get(title="xamsa")
        self.assertIn("Alisher Navoiy", book.content)
        self.assertIsNotNone(book.file)

    def test_regular_user_upload_forbidden(self):
        """Oddiy foydalanuvchi PDF yuklay olmasligini (403 Forbidden) tekshirish"""
        self.client.force_authenticate(user=self.regular_user)
        pdf_bytes = create_sample_pdf_bytes("Sinov")
        pdf_file = SimpleUploadedFile("test.pdf", pdf_bytes, content_type="application/pdf")

        response = self.client.post('/api/upload-pdf/', {'pdffile': pdf_file}, format='multipart')
        self.assertEqual(response.status_code, 403)

    def test_admin_upload_zip(self):
        """ZIP arxiv ichidagi PDF fayllar to'liq chiqarib olinishini tekshirish"""
        self.client.force_authenticate(user=self.admin)
        
        pdf_bytes = create_sample_pdf_bytes("ZIP Arxiv Ichidagi Kitob")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("book_inside.pdf", pdf_bytes)
        zip_buffer.seek(0)

        zip_file = SimpleUploadedFile("books.zip", zip_buffer.read(), content_type="application/zip")
        response = self.client.post('/api/upload-zip/', {'zipfile': zip_file}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Book.objects.filter(title="book_inside").exists())

    def test_ai_chat_with_extracted_content(self):
        """AI Chatbot view matnlarni xatosiz qayta ishlashini tekshirish"""
        self.client.force_authenticate(user=self.regular_user)
        Book.objects.create(
            title="O'tkan kunlar",
            author="Abdulla Qodiriy",
            content="Otabek va Kumush sevgi qissasi."
        )

        response = self.client.post('/api/chat/', {'message': "O'tkan kunlar haqida aytib ber"}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.data)

    def test_book_deletion_permissions(self):
        """Admin kitobni o'chira olishi, oddiy foydalanuvchi esa o'chira olmasligini tekshirish"""
        book = Book.objects.create(title="Vaqt va Inson", author="Tohir Malik")

        # Oddiy foydalanuvchi o'chirishga urinsa: 403 Forbidden
        self.client.force_authenticate(user=self.regular_user)
        res_user = self.client.delete(f'/api/books/{book.id}/')
        self.assertEqual(res_user.status_code, 403)

        # Admin o'chirishga urinsa: 204 No Content
        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.delete(f'/api/books/{book.id}/')
        self.assertEqual(res_admin.status_code, 204)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
