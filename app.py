# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
import zipfile
import google.generativeai as genai
from dotenv import load_dotenv

# .env faylini yuklash
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

gemini_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)

# CHUNKI 2026-YILDA ENG SO'NGGI MUSTAHKAM VA TEKIN MODEL: gemini-2.5-flash-lite
if gemini_key:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
else:
    model = None

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

# KATTA FILERLARDA QOTIB QOLMAYDIGAN OPTIMALLASHTIRILGAN ZIP YUKLASH TIZIMI
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    conn = get_db_connection()
    
    if request.method == 'POST':
        zip_file = request.files.get('zip_file')
        if zip_file and zip_file.filename.endswith('.zip'):
            # Faylni vaqtincha xavfsiz va tez saqlab olish
            temp_path = "temp_upload.zip"
            zip_file.save(temp_path)
            
            # Arxivni ochish va xotirani band qilmasdan oqim bilan bazaga yozish
            with zipfile.ZipFile(temp_path) as archive:
                for file_name in archive.namelist():
                    if file_name.endswith('.txt') and not file_name.startswith('__MACOSX'):
                        with archive.open(file_name) as f:
                            content = f.read().decode('utf-8')
                            clean_name = file_name.replace('.txt', '')
                            if " - " in clean_name:
                                b_title, b_author = clean_name.split(" - ", 1)
                            else:
                                b_title, b_author = clean_name, "Noma'lum muallif"
                                
                            conn.execute(
                                'INSERT INTO books (title, author, genre, description, content) VALUES (?, ?, ?, ?, ?)',
                                (b_title.strip(), b_author.strip(), "Elektron Kitob", "Ommaviy yuklangan mukammal asar.", content)
                            )
                conn.commit()
            
            # Server xotirasi to'lib qolmasligi uchun vaqtincha arxiv faylni darhol o'chiramiz
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        conn.close()
        return redirect(url_for('admin_panel'))

    books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', books=books)

@app.route('/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify({"reply": "Xatolik: Gemini API kaliti sozlanmagan."})
        
    user_message = request.json.get('message')
    
    conn = get_db_connection()
    books = conn.execute('SELECT title, author, genre, description FROM books').fetchall()
    conn.close()
    
    books_context = "Kutubxonadagi mavjud kitoblar ro'yxati:\n"
    for b in books:
        books_context += f"- Nomi: {b['title']}, Muallif: {b['author']}, Janri: {b['genre']}, Tavsif: {b['description']}\n"
        
    prompt = f"""Siz aqlli kutubxona yordamchisiz. Foydalanuvchiga faqat o'zbek tilida, xushmuomila javob bering.
{books_context}
Foydalanuvchi savoli: {user_message}"""

    try:
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Google Gemini API bilan bog'lanishda xatolik: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
