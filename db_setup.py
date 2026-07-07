# -*- coding: utf-8 -*-
import sqlite3
import os

# Ushbu fayl kutubxona ma'lumotlar bazasini va namunaviy kitoblarni yaratadi.

def init_db():
    db_path = 'library.db'
    
    # Toza muhit yaratish uchun agar eski baza fayli bo'lsa o'chiramiz
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Eski 'library.db' o'chirildi.")
        
    # Ma'lumotlar bazasiga ulanish (fayl bo'lmasa avtomatik yaratadi)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kitoblar jadvali:
    # id: tartib raqam (avtomatik o'sib boradi)
    # title: kitob nomi
    # author: muallif ismi
    # genre: kitob janri (masalan: Roman, Ertak, Fantastika)
    # description: kitob haqida qisqacha ma'lumot
    # db_setup.py ichidagi jadval yaratish qismi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT EXISTS,
        author TEXT,
        genre TEXT,
        description TEXT,
        content TEXT  -- Kitobning to'liq o'qiladigan matni shu yerda saqlanadi
    )
    ''')

    
    # AI chatbot tahlil qilishi uchun boshlang'ich namunaviy kitoblar ro'yxati
    sample_books = [
        ("O'tgan kunlar", 
         "Abdulla Qodiriy", 
         "Tarixiy Roman", 
         "XIX asr o'rtalaridagi Qo'qon xonligi davridagi o'zbek hayoti, an'analari va Otabek hamda Kumushning fojiaviy sevgisi tasvirlangan birinchi o'zbek romani."),
        
        ("Kichik shahzoda", 
         "Antuan de Sent-Ekzyuperi", 
         "Falsafiy Ertak", 
         "Boshqa kichik sayyoradan kelgan kichik shahzoda va uning cho'ldagi uchuvchi bilan do'stlashishi orqali hayot mantiqi va muhabbat qadri haqida yozilgan falsafiy ertak."),
        
        ("Ufq", 
         "Said Ahmad", 
         "Tarixiy Roman", 
         "Ikkinchi jahon urushi yillari va undan keyingi og'ir davrlarda o'zbek qishlog'i insonlarining hayoti va fojialarini ifodalovchi yirik roman-trilogiya."),
        
        ("Dunyoning ishlari", 
         "O'tkir Hoshimov", 
         "Qissa", 
         "Onaning muqaddas siymosi, o'z farzandlariga bo'lgan cheksiz mehri va oila qadriyatlarini sodda va yurakni larzaga soluvchi hikoyalar orqali tasvirlovchi ajoyib asar."),
         
        ("Fahrenheit 451", 
         "Rey Bredberi", 
         "Ilmiy-fantastika / Antiutopiya", 
         "Kelajakda kitoblar taqiqlangan va ularni yoqish odat tusiga kirgan jamiyat haqidagi antiutopiya. Asar insoniyat fikrlash va kitob mutolaasidan mahrum bo'lsa nima bo'lishini ko'rsatadi.")
    ]
    
    # Kitoblarni bazaga guruhlab yozish
    cursor.executemany('''
        INSERT INTO books (title, author, genre, description)
        VALUES (?, ?, ?, ?)
    ''', sample_books)
    
    # O'zgarishlarni saqlash va ulanishni yopish
    conn.commit()
    conn.close()
    print("Yangi 'library.db' bazasi muvaffaqiyatli yaratildi va 5 ta kitob kiritildi.")

if __name__ == '__main__':
    init_db()
