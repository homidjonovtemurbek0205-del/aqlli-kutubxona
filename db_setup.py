import sqlite3

def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Jadvalni yangi "content" ustuni bilan yaratish
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT EXISTS,
        author TEXT,
        genre TEXT,
        description TEXT,
        content TEXT
    )
    ''')
    
    # Eskidan qolgan ma'lumotlar bo'lsa tozalash
    cursor.execute('DELETE FROM books')
    
    # Haqiqiy o'qiladigan kitoblar matni (Namuna sifatida boblari bilan)
    namuna_kitoblar = [
        (
            "O'tkan kunlar",
            "Abdulla Qodiriy",
            "Tarixiy Roman",
            "XIX asr o'rtalaridagi Qo'qon xonligi davri, milliy an'analar va Otabek hamda Kumushning fojiaviy sevgisi tasvirlangan asar.",
            """1-BOB: TASHVISH xonasi.
Xonadon sohibi Otabek Marg'ilon safaridan qaytish taraddudida edi. Uning ko'nglida mudom bir g'ashlik, aytib bo'lmas bir sog'inch hukmron edi...
[Bu yerga asarning to'liq matni joylashadi. Hozircha namuna uchun shu qism yozildi]
2-BOB: KUMUSHNING KO'Z YOSHLARI.
Marg'ilonda tong otdi. Kumushbibi hovli chetidagi salqin ayvonda o'tirib, uzoqlarga termulardi..."""
        ),
        (
            "Alkimyogar",
            "Paulo Koelyo",
            "Falsafiy, Motivatsiya",
            "O'z orzulari ortidan ergashgan cho'pon bola Santyagoning sarguzashtlari va hayot falsafasi haqidagi ajoyib asar.",
            """1-BOB: CHO'PON BOLANING ORZULARI.
Santyago ismli cho'pon yigit o'z qo'ylari bilan Andalusiya dalalarida kezib yurar edi. U kechalari minorali eski cherkov xarobalarida tunar va g'ayrioddiy tushlar ko'rardi...
2-BOB: SAHRO SAFARI.
Misr ehromlari sari ketayotgan karvon sahro o'rtasida to'xtadi. Santyago u yerda haqiqiy Alkimyogarni uchratdi..."""
        )
    ]
    
    cursor.executemany(
        'INSERT INTO books (title, author, genre, description, content) VALUES (?, ?, ?, ?, ?)',
        namuna_kitoblar
    )
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
