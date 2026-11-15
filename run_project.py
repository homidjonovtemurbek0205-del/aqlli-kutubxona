# -*- coding: utf-8 -*-
"""
Aqlli Kutubxona Sayti (Smart Library with AI & Audiobooks)
Loyihani sozlovchi va ishga tushiruvchi skript.

Ushbu skript:
1. Zaruriy Python kutubxonalarini o'rnatadi.
2. Django ma'lumotlar bazasini sozlaydi va mavjud kitoblarni indekslaydi.
3. Serverni ishga tushiradi (http://127.0.0.1:8000/).
"""

import os
import sys
import subprocess

def install_dependencies():
    """Zaruriy kutubxonalarni o'rnatish"""
    print("\n1. Kutubxonalarni tekshirish va o'rnatish...")
    requirements_file = 'requirements.txt'
    if os.path.exists(requirements_file):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
            print(" - [MUVAFFAQIYATLI] Kutubxonalar tayyor.")
        except Exception as e:
            print(f" - [OGOHLANTIRISH] pip install muammo: {e}")

def setup_database():
    """Ma'lumotlar bazasini sozlash (Django SQLite)"""
    print("\n2. Ma'lumotlar bazasini sozlash (Django Migrations)...")
    try:
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print(" - [MUVAFFAQIYATLI] Migratsiyalar bajarildi.")
    except Exception as e:
        print(f" - [XATOLIK] Migratsiyada xatolik: {e}")
        sys.exit(1)

    print("\n3. Boshlang'ich foydalanuvchilar va kitoblarni indekslash...")
    try:
        subprocess.run([sys.executable, "manage.py", "setup_library"], check=True)
        print(" - [MUVAFFAQIYATLI] Admin va kitoblar fondi sozlandi.")
    except Exception as e:
        print(f" - [OGOHLANTIRISH] setup_library: {e}")

def run_server():
    """Django serverini ishga tushirish"""
    print("\n4. Server ishga tushirilmoqda...")
    print("=" * 60)
    print("  AQLLI KUTUBXONA TIZIMI TAYYOR!")
    print("  --> http://127.0.0.1:8000/")
    print("  Admin hisobi:  admin@library.com  |  Parol: admin123")
    print("  Kitobxon:      user@library.com   |  Parol: user123")
    print("=" * 60)
    print("Serverni to'xtatish uchun CTRL + C tugmalarini bosing.\n")

    try:
        subprocess.run([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"])
    except KeyboardInterrupt:
        print("\nServer to'xtatildi.")

if __name__ == '__main__':
    print("=" * 60)
    print("  AQLLI KUTUBXONA TIZIMI - ISHGA TUSHIRISH")
    print("=" * 60)
    install_dependencies()
    setup_database()
    run_server()
