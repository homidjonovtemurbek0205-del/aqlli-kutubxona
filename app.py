# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import os
import google.generativeai as genai
from dotenv import load_dotenv
import zipfile
import fitz  # PyMuPDF
import uuid
import shutil

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'zip'}
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

gemini_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super-secret-key' # Iltimos, buni o'zgartiring

if gemini_key:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
else:
    model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

if not os.path.exists('library.db'):
    from db_setup import init_db
    init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/read/<int:book_id>')
def read_book(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    if book is None:
        return "Kitob topilmadi", 404
    return render_template('read.html', book=book)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST' and 'zipfile' in request.files:
        file = request.files['zipfile']
        if file.filename == '':
            flash('Hech qanday fayl tanlanmadi', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + ".zip")
            file.save(zip_path)

            extract_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_' + str(uuid.uuid4()))
            os.makedirs(extract_folder)

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)
                
                conn = get_db_connection()
                added_books = 0
                for root, _, files in os.walk(extract_folder):
                    for filename in files:
                        if filename.lower().endswith('.pdf'):
                            pdf_path = os.path.join(root, filename)
                            doc = fitz.open(pdf_path)
                            content = ""
                            for page in doc:
                                content += page.get_text()
                            doc.close()
                            
                            title = os.path.splitext(filename)[0]
                            # Xatolikni tuzatish: Qaysi ustunlarga yozilayotganini aniq ko'rsatish
                            conn.execute('INSERT INTO books (title, author, genre, description, content) VALUES (?, ?, ?, ?, ?)', (title, 'Noma\'lum', 'PDF', f'{title} kitobining elektron nusxasi.', content))
                            added_books += 1
                conn.commit()
                conn.close()
                flash(f'{added_books} ta PDF kitob muvaffaqiyatli bazaga qo\'shildi!', 'success')
            except Exception as e:
                flash(f'Xatolik yuz berdi: {e}', 'danger')
            finally:
                # Vaqtinchalik fayl va papkalarni tozalash
                if os.path.exists(zip_path): os.remove(zip_path)
                if os.path.exists(extract_folder): shutil.rmtree(extract_folder)
            
            return redirect(url_for('admin_panel'))

    return render_template('admin.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify({"reply": "Xatolik: Gemini API kaliti sozlanmagan."})
    user_message = request.json.get('message')
    conn = get_db_connection()
    # Endi to'liq kontentni ham olamiz
    books = conn.execute('SELECT id, title, author, genre, description, content FROM books').fetchall()
    conn.close()
    
    books_context = "Kutubxonadagi mavjud kitoblar ro'yxati:\n"
    for b in books:
        # AI uchun kontekstni to'liqroq qilamiz
        books_context += f"""---
ID: {b['id']}
Nomi: {b['title']}
Muallif: {b['author']}
Janri: {b['genre']}
Qisqacha tavsif: {b['description']}
To'liq matni (qisqartirilgan): {b['content'][:1500]}... 
---\n"""
        
    prompt = f"""Siz "Aqlli Kutubxona"ning AI yordamchisisiz. Sizning vazifalaringiz:
1. Foydalanuvchi so'ragan janr yoki mavzudagi kitoblarni tavsiya qilish.
2. Foydalanuvchi biror kitob haqida (masalan, "Alkimyogar" mazmuni qanaqa?) deb so'rasa, yuqoridagi "To'liq matni" qismidan foydalanib, uning mazmunini aytib berish.
3. Foydalanuvchi bilan o'qigan kitoblari bo'yicha savol-javob qilish. Masalan, "O'tkan kunlar asaridagi bosh qahramon kim?".
4. Foydalanuvchi kitob qidirsa, unga yordam berish.
Javoblaringizni doim o'zbek tilida, xushmuomila va aniq bering.

MAVJUD KITOBLAR MA'LUMOTI:
{books_context}
Foydalanuvchi savoli: {user_message}"""

    try:
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Google Gemini API bilan bog'lanishda xatolik: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
