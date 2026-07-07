# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
import google.generativeai as genai
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

gemini_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)

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

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        # Brauzerdan kelgan tayyor kitob ma'lumotlarini qabul qilish
        data = request.json
        if data and 'books' in data:
            conn = get_db_connection()
            for book in data['books']:
                conn.execute(
                    'INSERT INTO books (title, author, genre, description, content) VALUES (?, ?, ?, ?, ?)',
                    (book['title'], book['author'], book['genre'], book['description'], book['content'])
                )
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": f"{len(data['books'])} ta kitob muvaffaqiyatli qo'shildi!"})
        return jsonify({"status": "error", "message": "Ma'lumot topilmadi"}), 400

    return render_template('admin.html')

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
