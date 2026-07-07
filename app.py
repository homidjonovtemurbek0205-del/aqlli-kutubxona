# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import os
from dotenv import load_dotenv

# .env faylini absolyut yo'l orqali yuklash (qayerdan chaqirilishidan qat'i nazar ishlashi uchun)
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

print(f"[*] Tizim sozlamalari yuklanmoqda... .env fayli: {dotenv_path}")
print(f"[*] GEMINI_API_KEY yuklandimi: {bool(os.getenv('GEMINI_API_KEY'))}")

app = Flask(__name__)

def get_db_connection():
    # SQLite bazasi bilan aloqa o'rnatish
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row  # Qatorlarni lug'at (dict) formatida qaytarish uchun
    return conn

def get_ai_response(user_query, books_list):
    """
    Foydalanuvchining so'rovi (query) va bazadagi kitoblar ro'yxatini (books_list) oladi.
    Tizimda API kalit borligiga qarab mos API orqali javob oladi, 
    agar kalit bo'lmasa, mahalliy matnli qidiruv algoritmi (fallback) yordamida javob beradi.
    """
    # Atrof-muhit o'zgaruvchilaridan kalitlarni olish
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Bazadagi kitoblar ro'yxatidan AI tushunadigan matnli kontekst tayyorlash
    books_context = "Kutubxonamizdagi mavjud kitoblar ro'yxati:\n"
    for book in books_list:
        books_context += f"- ID: {book['id']}, Nomi: \"{book['title']}\", Muallifi: {book['author']}, Janri: {book['genre']}. Tavsif: {book['description']}\n"
    
    # AI ga qanday rol o'ynashini tushuntiruvchi yo'riqnoma (System Prompt)
    system_prompt = (
        "Siz aqlli kutubxona chatbotisiz. Foydalanuvchiga faqat yuqorida keltirilgan kitoblar ro'yxatidan "
        "tavsiyalar bering. Agar foydalanuvchi so'ragan janr yoki mavzudagi kitob topilmasa, bazada yo'qligini ayting "
        "va o'rniga boshqa mavjud kitoblardan mosini tavsiya qiling. Javoblaringiz samimiy va chiroyli o'zbek tilida bo'lsin. "
        "Tanlangan kitoblarni nima uchun tavsiya qilayotganingizni bazadagi tavsifidan kelib chiqib qisqa tushuntiring."
    )
    
    # Hujjat tuzilishi
    full_prompt = f"{system_prompt}\n\n{books_context}\n\nFoydalanuvchi savoli: {user_query}"

    # 1. Google Gemini API ni tekshirish va ishlatish
    if gemini_key:
        try:
            import google.generativeai as genai
            from google.api_core.client_options import ClientOptions
            
            # API versiyasini 'v1' va endpointni generativelanguage.googleapis.com qilib sozlash
            genai.configure(api_key=gemini_key)
            
            # Barqaror va eng so'nggi Gemini modelini yuklash (gemini-2.5-flash)
            model = genai.GenerativeModel('gemini-3.5-flash')
            
            # AI orqali javob matnini yaratish
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Google Gemini API bilan bog'lanishda xatolik: {str(e)}"

    # 2. OpenAI API ni tekshirish va ishlatish (Agar Gemini kaliti yo'q, lekin OpenAI bo'lsa)
    elif openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            messages = [
                {"role": "system", "content": f"{system_prompt}\n\n{books_context}"},
                {"role": "user", "content": user_query}
            ]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI API bilan bog'lanishda xatolik: {str(e)}"
            
    # 3. Mahalliy Algoritm (Agar hech qanday API kalit kiritilmagan bo'lsa - Crash bo'lmasligi uchun)
    else:
        q = user_query.lower()
        recommendations = []
        
        # Oddiy kalit so'zlar bo'yicha qidiruv logikasi
        for book in books_list:
            title = book['title'].lower()
            author = book['author'].lower()
            genre = book['genre'].lower()
            desc = book['description'].lower()
            
            # Agar foydalanuvchi yozgan so'z kitob tafsilotlarida uchrsa
            if q in title or q in author or q in genre or q in desc or \
               ("tarix" in q and "tarix" in genre) or \
               ("ertak" in q and "ertak" in genre) or \
               ("roman" in q and "roman" in genre) or \
               ("fantastika" in q and "fantastika" in genre):
                recommendations.append(book)
        
        # Foydalanuvchiga API kalitni sozlash kerakligi haqida ogohlantirish beramiz
        warning_msg = (
            "(⚠️ Eslatma: Gemini API kaliti sozlanmagan. To'liq AI tavsiyalarini ko'rish uchun "
            "loyiha papkasidagi '.env' fayliga 'GEMINI_API_KEY=API_KALIT' deb yozib qo'ying.)\n\n"
        )
        
        if recommendations:
            res = warning_msg + "Mahalliy qidiruv natijasida quyidagi kitoblar topildi:\n"
            for b in recommendations:
                res += f"\n📖 **{b['title']}** ({b['author']}) - Janri: {b['genre']}\nTavsif: {b['description']}\n"
            return res
        else:
            res = warning_msg + "Kutubxonada siz aytgan mavzuga oid mos kitob topilmadi. Hozircha quyidagilar mavjud:\n"
            for b in books_list:
                res += f"- **{b['title']}** (Muallif: {b['author']}, Janri: {b['genre']})\n"
            return res

# 1. BOSH SAHIFA: Kitoblar ro'yxatini chiqarish
@app.route('/')
def index():
    conn = get_db_connection()
    # Barcha kitoblarni bazadan tartib bilan o'qib olish
    books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
    conn.close()
    # HTML shablonga kitoblar ma'lumotini uzatish
    return render_template('index.html', books=books)

# 2. KITOB QO'SHISH ROUTE: Post so'rovini qabul qiladi
@app.route('/add', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    description = request.form.get('description')
    
    # Maydonlar bo'sh emasligini tekshiramiz
    if title and author and genre and description:
        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author, genre, description) VALUES (?, ?, ?, ?)',
                     (title, author, genre, description))
        conn.commit()
        conn.close()
        
    return redirect('/')

# 3. KITOB O'CHIRISH ROUTE: Baza jadvalidan ID bo'yicha o'chirish
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return redirect('/')

# 4. CHAT ROUTE: AJAX so'rovlariga JSON javob beradi
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Bazadagi kitoblarni olish
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    
    # AI funksiyasini chaqirish
    ai_reply = get_ai_response(user_message, books)
    
    return jsonify({"reply": ai_reply})

if __name__ == '__main__':
    # Flask ilovasini localhost (127.0.0.1) port 5000 da ishga tushiramiz
    app.run(debug=True, port=5000)
