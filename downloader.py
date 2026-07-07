import os
import requests
import zipfile
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# ANIQ KITOB RO'YXATI TURGAN SAHIFA MANZILI
url = "https://ziyouz.com"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

print("[*] Ziyouz platformasi xavfsiz tizim orqali skaner qilinmoqda...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Barcha yuklab olish havolalarini qidirish
links = soup.find_all('a')
download_urls = []

for link in links:
    href = link.get('href', '')
    # Ziyouz saytining ichki yuklash tizimi ssilkalarini ushlash
    if "com_jdownloads" in href or "download" in href or href.endswith('.mp3') or href.endswith('.pdf'):
        if not href.startswith('http'):
            href = "https://ziyouz.com" + href
        if href not in download_urls:
            download_urls.append(href)

print(f"[+] Sahifada jami {len(download_urls)} ta kitob qismi aniqlandi.")

# Fayllarni yuklash funksiyasi
def download_file(file_url):
    try:
        file_name = file_url.split('/')[-1].split('?')[0] or "kitob_qismi.mp3"
        # Belgilarni tozalash
        for char in ['?', '=', '&', '/', '\\', '*', ':', '"', '<', '>', '|']:
            file_name = file_name.replace(char, '_')
            
        if not (file_name.endswith('.mp3') or file_name.endswith('.pdf')):
            file_name += ".mp3"
            
        print(f"[>] Yuklanmoqda: {file_name}")
        file_data = requests.get(file_url, headers=headers, timeout=15).content
        with open(file_name, 'wb') as f:
            f.write(file_data)
        return file_name
    except Exception as e:
        print(f"[X] Xatolik: {file_url} yuklanmadi. Sababi: {e}")
        return None

# BIR VAQTNING O'ZIDA PARALLEL YUKLASH (KUNLAR KETMAYDI, 1 MINUTDA YUKLAYDI)
print("[*] Ommaviy va parallel yuklash boshlandi. Iltimos kuting...")
downloaded_files = []
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(download_file, download_urls)
    for res in results:
        if res:
            downloaded_files.append(res)

# HAMMASINI BITTA TAYYOR ZIP ARXIVGA JOYLASHTIRISH
if downloaded_files:
    zip_name = "ommaviy_kitoblar.zip"
    print(f"\n[*] Yuklangan barcha {len(downloaded_files)} ta fayl {zip_name} arxiviga joylashtirilmoqda...")
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in downloaded_files:
            if os.path.exists(file):
                zipf.write(file)
                os.remove(file) # Kompyuter toza qolishi uchun vaqtincha fayllarni o'chiramiz
    print(f"[🎉] TAYYOR! Barcha kitoblar '{zip_name}' fayliga bittada yig'ildi!")
else:
    print("[X] Hech qanday fayl yuklanmadi.")
