# -*- coding: utf-8 -*-
"""
Aqlli Kutubxona Sayti (Library Management System with AI)
Loyihani sozlovchi va ishga tushiruvchi skript.

Ushbu skript:
1. Kerakli Python kutubxonalarini o'rnatadi.
2. Ma'lumotlar bazasini (agar mavjud bo'lmasa) yaratadi.
3. Flask serverini ishga tushiradi.
"""

import os
import sys
import subprocess

def install_dependencies():
    """Zaruriy kutubxonalarni o'rnatish"""
    print("\n1. Kutubxonalarni o'rnatish (pip install)...")

    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        print(f" - [XATOLIK] '{requirements_file}' fayli topilmadi. Iltimos, uni yarating.")
        sys.exit(1)
        
    try:
        # Endi kutubxonalarni requirements.txt faylidan o'rnatamiz
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", requirements_file], check=True)
        print(" - [MUVAFFAQIYATLI] Kutubxonalar o'rnatildi.")
    except Exception as e:
        print(f" - [XATOLIK] Kutubxonalarni o'rnatishda muammo bo'ldi: {str(e)}")
        sys.exit(1)

def setup_database():
    """Ma'lumotlar bazasini yaratish"""
    print("\n2. Ma'lumotlar bazasini sozlash (SQLite)...")
    if not os.path.exists('library.db'):
        print(" - 'library.db' topilmadi, yangisi yaratilmoqda...")
        try:
            subprocess.run([sys.executable, "db_setup.py"], check=True)
            print(" - [MUVAFFAQIYATLI] Ma'lumotlar bazasi yaratildi.")
        except Exception as e:
            print(f" - [XATOLIK] Baza yaratishda muammo bo'ldi: {str(e)}")
            sys.exit(1)
    else:
        print(" - [MAVJUD] 'library.db' fayli allaqachon mavjud.")

def run_flask_server():
    """Flask ilovasini ishga tushirish"""
    print("\n3. Flask serverini ishga tushirish...")
    print("=" * 60)
    print("Saytni ko'rish uchun quyidagi manzilni brauzerda oching:")
    print("--> http://127.0.0.1:5000/")
    print("Serverni o'chirish uchun terminalda CTRL + C tugmalarini bosing.")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nServer to'xtatildi.")

if __name__ == '__main__':
    print("=" * 60)
    print("  AQLLI KUTUBXONA TIZIMI - AVTOMATIK SOZLASH VA ISHGA TUSHIRISH")
    print("=" * 60)
    install_dependencies()
    setup_database()
    run_flask_server()
