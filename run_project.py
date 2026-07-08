# -*- coding: utf-8 -*-
"""
Aqlli Kutubxona Sayti (Library Management System with AI)
Avtomatik o'rnatuvchi va ishga tushiruvchi boshqaruvchi skript.

Ushbu skript:
1. templates/index.html, db_setup.py, app.py va .env fayllarini yaratadi.
2. Kerakli Python kutubxonalarini o'rnatadi.
3. Ma'lumotlar bazasini yaratadi.
4. Flask serverini ishga tushiradi.
"""

import os
import sys
import subprocess

# Loyiha fayllari joylashadigan asosiy katalogni aniqlash
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

# HTML/CSS shablon (index.html) - Premium dizaynda
HTML_CONTENT = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aqlli Kutubxona | AI Tavsiyalari</title>
    <!-- Google Fonts va FontAwesome Ulanishi -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        /* Premium Glassmorphism & Dark Mode Dizayn Tizimi */
        :root {
            --bg-gradient: linear-gradient(135deg, #0d0b18 0%, #15102a 50%, #080610 100%);
            --panel-bg: rgba(255, 255, 255, 0.03);
            --panel-border: rgba(255, 255, 255, 0.08);
            --primary: #8b5cf6; /* Violet */
            --primary-glow: rgba(139, 92, 246, 0.4);
            --secondary: #14b8a6; /* Teal */
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --danger: #ef4444;
            --font: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--font);
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Navigatsiya */
        header {
            padding: 1.5rem 2rem;
            border-bottom: 1px solid var(--panel-border);
            backdrop-filter: blur(12px);
            background: rgba(13, 11, 24, 0.5);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #a78bfa, var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .logo i {
            color: var(--primary);
            -webkit-text-fill-color: initial;
        }

        /* Asosiy Konteyner */
        .container {
            max-width: 1200px;
            width: 100%;
            margin: 2rem auto;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 2rem;
            flex-grow: 1;
        }

        @media (max-width: 900px) {
            .container {
                grid-template-columns: 1fr;
            }
        }

        /* Glassmorphic Panel (Card) */
        .glass-panel {
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Sarlavhalar */
        h2 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #ffffff;
        }

        h2 i {
            color: var(--secondary);
        }

        /* Formalar */
        .form-group {
            margin-bottom: 1.25rem;
        }

        .form-group label {
            display: block;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 500;
        }

        .form-control {
            width: 100%;
            padding: 0.75rem 1rem;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--panel-border);
            border-radius: 10px;
            color: #ffffff;
            font-family: var(--font);
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 8px var(--primary-glow);
        }

        textarea.form-control {
            resize: vertical;
            min-height: 100px;
        }

        /* Tugmalar */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 10px;
            font-family: var(--font);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            width: 100%;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%);
            color: #ffffff;
            box-shadow: 0 4px 14px var(--primary-glow);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        }

        .btn-danger-icon {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.2);
            padding: 0.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            width: auto;
        }

        .btn-danger-icon:hover {
            background: var(--danger);
            color: white;
        }

        /* Kitoblar Ro'yxati */
        .books-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
        }

        .book-card {
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            position: relative;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .book-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        }

        .book-genre {
            align-self: flex-start;
            font-size: 0.75rem;
            background: rgba(20, 184, 166, 0.1);
            color: var(--secondary);
            padding: 0.25rem 0.6rem;
            border-radius: 20px;
            margin-bottom: 0.75rem;
            font-weight: 600;
        }

        .book-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.25rem;
        }

        .book-author {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .book-desc {
            font-size: 0.85rem;
            color: #d1d5db;
            line-height: 1.4;
            flex-grow: 1;
            margin-bottom: 1.25rem;
        }

        .book-footer {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            border-top: 1px solid var(--panel-border);
            padding-top: 0.75rem;
        }

        /* SUZUVCHI AI CHATBOT OYNASI */
        .chat-widget {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }

        /* Chat ochish tugmasi */
        .chat-toggle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%);
            box-shadow: 0 6px 20px var(--primary-glow);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            position: relative;
        }

        .chat-toggle:hover {
            transform: scale(1.1);
        }

        .chat-toggle .pulse {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: var(--primary);
            opacity: 0.4;
            animation: pulse-animation 2s infinite;
            z-index: -1;
        }

        @keyframes pulse-animation {
            0% { transform: scale(1); opacity: 0.4; }
            100% { transform: scale(1.5); opacity: 0; }
        }

        /* Chat oynasi */
        .chat-window {
            width: 380px;
            height: 500px;
            background: #110e24;
            border: 1px solid var(--panel-border);
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            margin-bottom: 1rem;
            transform: translateY(20px) scale(0.9);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(20px);
        }

        .chat-window.active {
            transform: translateY(0) scale(1);
            opacity: 1;
            pointer-events: auto;
        }

        .chat-header {
            background: linear-gradient(to right, #1a1635, #231d45);
            padding: 1rem 1.25rem;
            border-bottom: 1px solid var(--panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            color: #ffffff;
        }

        .chat-header-title i {
            color: var(--secondary);
        }

        .chat-close-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 1.1rem;
            transition: color 0.2s;
        }

        .chat-close-btn:hover {
            color: #ffffff;
        }

        /* Xabarlar maydoni */
        .chat-messages {
            flex-grow: 1;
            padding: 1.25rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            scroll-behavior: smooth;
        }

        /* Chat scrollbari */
        .chat-messages::-webkit-scrollbar {
            width: 5px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: transparent;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .message {
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 14px;
            font-size: 0.85rem;
            line-height: 1.4;
            word-wrap: break-word;
        }

        .message-bot {
            background: rgba(255, 255, 255, 0.05);
            color: #e5e7eb;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }

        .message-user {
            background: var(--primary);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }

        /* Tezkor takliflar tugmalari */
        .quick-suggestions {
            padding: 0.5rem 1rem;
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            border-top: 1px solid rgba(255, 255, 255, 0.03);
        }

        .suggestion-btn {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--panel-border);
            color: #d1d5db;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .suggestion-btn:hover {
            background: rgba(139, 92, 246, 0.15);
            border-color: var(--primary);
            color: white;
        }

        /* Yozish/Yuborish qismi */
        .chat-input-area {
            padding: 1rem;
            border-top: 1px solid var(--panel-border);
            display: flex;
            gap: 0.5rem;
            background: #110e24;
        }

        .chat-input {
            flex-grow: 1;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--panel-border);
            padding: 0.65rem 1rem;
            border-radius: 10px;
            color: white;
            font-family: var(--font);
            font-size: 0.85rem;
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--primary);
        }

        .chat-send-btn {
            background: var(--primary);
            color: white;
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }

        .chat-send-btn:hover {
            background: #7c3aed;
        }

        .typing-indicator {
            display: inline-flex;
            gap: 4px;
            align-items: center;
            padding: 4px 8px;
        }

        .typing-dot {
            width: 6px;
            height: 6px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out both;
        }

        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>

    <!-- Sarlavha -->
    <header>
        <div class="logo">
            <i class="fa-solid fa-graduation-cap"></i>
            <span>SmartLibrary</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">
            <i class="fa-solid fa-robot" style="color: var(--secondary)"></i> AI Integratsiyasi
        </div>
    </header>

    <!-- Asosiy Grid -->
    <div class="container">
        
        <!-- Chap tomonda: Kitob qo'shish paneli -->
        <div class="glass-panel" style="height: fit-content;">
            <h2><i class="fa-solid fa-circle-plus"></i> Yangi Kitob Qo'shish</h2>
            <form action="/add" method="POST">
                <div class="form-group">
                    <label for="title">Kitob Nomi</label>
                    <input type="text" id="title" name="title" class="form-control" placeholder="Masalan: O'tgan kunlar" required>
                </div>
                <div class="form-group">
                    <label for="author">Muallif</label>
                    <input type="text" id="author" name="author" class="form-control" placeholder="Masalan: Abdulla Qodiriy" required>
                </div>
                <div class="form-group">
                    <label for="genre">Janri</label>
                    <input type="text" id="genre" name="genre" class="form-control" placeholder="Masalan: Tarixiy Roman" required>
                </div>
                <div class="form-group">
                    <label for="description">Qisqacha Tavsifi</label>
                    <textarea id="description" name="description" class="form-control" placeholder="Kitob syujeti va mantiqiy mazmuni haqida..." required></textarea>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fa-solid fa-paper-plane"></i> Baza Fayliga Qo'shish
                </button>
            </form>
        </div>

        <!-- O'ng tomonda: Kitoblar ro'yxati -->
        <div class="glass-panel">
            <h2><i class="fa-solid fa-book-open"></i> Mavjud Kitoblar Ro'yxati</h2>
            
            {% if not books %}
                <div style="text-align: center; color: var(--text-muted); padding: 3rem 0;">
                    <i class="fa-solid fa-book" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <p>Hozircha kutubxonada kitoblar yo'q. Chap tarafdagi forma orqali qo'shing!</p>
                </div>
            {% else %}
                <div class="books-grid">
                    {% for book in books %}
                        <div class="book-card">
                            <span class="book-genre">{{ book.genre }}</span>
                            <div class="book-title">{{ book.title }}</div>
                            <div class="book-author"><i class="fa-regular fa-user"></i> {{ book.author }}</div>
                            <div class="book-desc">{{ book.description }}</div>
                            <div class="book-footer">
                                <form action="/delete/{{ book.id }}" method="POST" onsubmit="return confirm('Kitobni o\\'chirishni xohlaysizmi?')">
                                    <button type="submit" class="btn-danger-icon" title="O'chirish">
                                        <i class="fa-solid fa-trash-can"></i>
                                    </button>
                                </form>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>
    </div>

    <!-- AI CHATBOT UI -->
    <div class="chat-widget">
        <!-- Chat Oynasi -->
        <div class="chat-window" id="chatWindow">
            <div class="chat-header">
                <div class="chat-header-title">
                    <i class="fa-solid fa-robot"></i>
                    <span>Kutubxona Yordamchisi (AI)</span>
                </div>
                <button class="chat-close-btn" onclick="toggleChat()"><i class="fa-solid fa-xmark"></i></button>
            </div>
            
            <!-- Xabarlar maydoni -->
            <div class="chat-messages" id="chatMessages">
                <div class="message message-bot">
                    Assalomu alaykum! Men kutubxona AI yordamchisiman. Bazadagi kitoblar asosida sizga tavsiyalar bera olaman. Masalan, mendan "Menga tarixiy asar topib ber" deb so'rab ko'ring!
                </div>
            </div>

            <!-- Tezkor takliflar -->
            <div class="quick-suggestions">
                <button class="suggestion-btn" onclick="sendQuickMessage('Menga tarixiy kitob tavsiya et')">Tarixiy kitoblar</button>
                <button class="suggestion-btn" onclick="sendQuickMessage('Falsafiy yoki ertak tabiatli asar bormi?')">Falsafiy/Ertak</button>
                <button class="suggestion-btn" onclick="sendQuickMessage('Barcha kitoblar ro\\'yxati')">Barcha kitoblar</button>
            </div>

            <!-- Yozish qismi -->
            <div class="chat-input-area">
                <input type="text" id="chatInput" class="chat-input" placeholder="Xabaringizni yozing..." onkeypress="handleKeyPress(event)">
                <button class="chat-send-btn" onclick="sendMessage()"><i class="fa-solid fa-arrow-up"></i></button>
            </div>
        </div>

        <!-- Chatni ochish tugmasi -->
        <button class="chat-toggle" onclick="toggleChat()">
            <div class="pulse"></div>
            <i class="fa-solid fa-comments"></i>
        </button>
    </div>

    <script>
        // Chat oynasini ko'rsatish/yashirish
        function toggleChat() {
            const chatWindow = document.getElementById('chatWindow');
            chatWindow.classList.toggle('active');
            if (chatWindow.classList.contains('active')) {
                document.getElementById('chatInput').focus();
            }
        }

        // Enter tugmasini bosganda xabar yuborish
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Tezkor taklif tugmalarini bosganda xabar yuborish
        function sendQuickMessage(text) {
            document.getElementById('chatInput').value = text;
            sendMessage();
        }

        // Xabar matnini formatlash (Markdown formatidagi ** va yangi qatorlarni chiroyli qilish)
        function formatMessageText(text) {
            // Qalin yozuvlar: **matn** -> <strong>matn</strong>
            let formatted = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            // Yangi qatorlar: \\n -> <br>
            formatted = formatted.replace(/\\n/g, '<br>');
            return formatted;
        }

        // Xabar yuborish logikasi
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const messageText = input.value.trim();
            if (!messageText) return;

            const chatMessages = document.getElementById('chatMessages');

            // 1. Foydalanuvchi xabarini ekranga chiqarish
            const userDiv = document.createElement('div');
            userDiv.className = 'message message-user';
            userDiv.textContent = messageText;
            chatMessages.appendChild(userDiv);

            // Inputni tozalash
            input.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // 2. AI yozayotganini ko'rsatish (Typing Indicator)
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message message-bot';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // 3. Flask backendga AJAX so'rov yuborish
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: messageText })
            })
            .then(response => response.json())
            .then(data => {
                // Yozish indikatorini o'chirish
                const indicator = document.getElementById('typingIndicator');
                if (indicator) indicator.remove();

                // AI javobini chiqarish
                const botDiv = document.createElement('div');
                botDiv.className = 'message message-bot';
                botDiv.innerHTML = formatMessageText(data.reply);
                chatMessages.appendChild(botDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                console.error('Xatolik yuz berdi:', error);
                const indicator = document.getElementById('typingIndicator');
                if (indicator) indicator.remove();

                const errorDiv = document.createElement('div');
                errorDiv.className = 'message message-bot';
                errorDiv.style.color = '#ef4444';
                errorDiv.textContent = 'Uzr, server bilan aloqa o\\'rnatib bo\\'lmadi.';
                chatMessages.appendChild(errorDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });
        }

        // OVOZLI O'QISH FUNKSIYASI
        function readAloud(text) {
            // Agar boshqa narsa o'qilayotgan bo'lsa, to'xtatish
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                return; // Ikkinchi marta bosganda to'xtatadi
            }
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'uz-UZ'; // O'zbek tilini belgilash
            utterance.rate = 0.9; // O'qish tezligi
            
            // O'qishni boshlash
            window.speechSynthesis.speak(utterance);
        }
    </script>
</body>
</html>
"""

# Ma'lumotlar bazasini sozlash skripti (db_setup.py)
DB_SETUP_CONTENT = """# -*- coding: utf-8 -*-
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            description TEXT NOT NULL
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
"""

# Flask Ilovasi (app.py) - SQLite va AI bilan aloqa logikasi
APP_CONTENT = """# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import os
from dotenv import load_dotenv

# .env faylidagi API kalitlarini (Gemini/OpenAI) tizim xotirasiga yuklash
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    # SQLite bazasi bilan aloqa o'rnatish
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row  # Qatorlarni lug'at (dict) formatida qaytarish uchun
    return conn

def get_ai_response(user_query, books_list):
    \"\"\"
    Foydalanuvchining so'rovi (query) va bazadagi kitoblar ro'yxatini (books_list) oladi.
    Tizimda API kalit borligiga qarab mos API orqali javob oladi, 
    agar kalit bo'lmasa, mahalliy matnli qidiruv algoritmi (fallback) yordamida javob beradi.
    \"\"\"
    # Atrof-muhit o'zgaruvchilaridan kalitlarni olish
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Bazadagi kitoblar ro'yxatidan AI tushunadigan matnli kontekst tayyorlash
    books_context = "Kutubxonamizdagi mavjud kitoblar ro'yxati:\\n"
    for book in books_list:
        books_context += f"- ID: {book['id']}, Nomi: \\"{book['title']}\\", Muallifi: {book['author']}, Janri: {book['genre']}. Tavsif: {book['description']}\\n"
    
    # AI ga qanday rol o'ynashini tushuntiruvchi yo'riqnoma (System Prompt)
    system_prompt = (
        "Siz aqlli kutubxona chatbotisiz. Foydalanuvchiga faqat yuqorida keltirilgan kitoblar ro'yxatidan "
        "tavsiyalar bering. Agar foydalanuvchi so'ragan janr yoki mavzudagi kitob topilmasa, bazada yo'qligini ayting "
        "va o'rniga boshqa mavjud kitoblardan mosini tavsiya qiling. Javoblaringiz samimiy va chiroyli o'zbek tilida bo'lsin. "
        "Tanlangan kitoblarni nima uchun tavsiya qilayotganingizni bazadagi tavsifidan kelib chiqib qisqa tushuntiring."
    )
    
    # Hujjat tuzilishi
    full_prompt = f"{system_prompt}\\n\\n{books_context}\\n\\nFoydalanuvchi savoli: {user_query}"

    # 1. Google Gemini API ni tekshirish va ishlatish
    if gemini_key:
        try:
            import google.generativeai as genai
            from google.api_core.client_options import ClientOptions
            
            # API versiyasini 'v1' va endpointni generativelanguage.googleapis.com qilib sozlash
            client_options = ClientOptions(
                api_endpoint="generativelanguage.googleapis.com",
                api_version="v1"
            )
            genai.configure(api_key=gemini_key, client_options=client_options)
            
            # Barqaror va eng so'nggi Gemini modelini yuklash (gemini-2.5-flash)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
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
                {"role": "system", "content": f"{system_prompt}\\n\\n{books_context}"},
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
            if q in title or q in author or q in genre or q in desc or \\
               ("tarix" in q and "tarix" in genre) or \\
               ("ertak" in q and "ertak" in genre) or \\
               ("roman" in q and "roman" in genre) or \\
               ("fantastika" in q and "fantastika" in genre):
                recommendations.append(book)
        
        # Foydalanuvchiga API kalitni sozlash kerakligi haqida ogohlantirish beramiz
        warning_msg = (
            "(⚠️ Eslatma: Gemini API kaliti sozlanmagan. To'liq AI tavsiyalarini ko'rish uchun "
            "loyiha papkasidagi '.env' fayliga 'GEMINI_API_KEY=API_KALIT' deb yozib qo'ying.)\\n\\n"
        )
        
        if recommendations:
            res = warning_msg + "Mahalliy qidiruv natijasida quyidagi kitoblar topildi:\\n"
            for b in recommendations:
                res += f"\\n📖 **{b['title']}** ({b['author']}) - Janri: {b['genre']}\\nTavsif: {b['description']}\\n"
            return res
        else:
            res = warning_msg + "Kutubxonada siz aytgan mavzuga oid mos kitob topilmadi. Hozircha quyidagilar mavjud:\\n"
            for b in books_list:
                res += f"- **{b['title']}** (Muallif: {b['author']}, Janri: {b['genre']})\\n"
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
"""

# .env shabloni
ENV_CONTENT = """# Google Gemini API kalitini shu yerga yozing:
GEMINI_API_KEY=

# Yoki OpenAI API kalitini yozing (ixtiyoriy):
OPENAI_API_KEY=
"""

def create_files():
    """Loyiha uchun kerakli papka va fayllarni yaratish"""
    print("1. Loyiha strukturasini yaratish...")
    
    # templates papkasini yaratish
    os.makedirs('templates', exist_ok=True)
    
    # templates/index.html yozish
    index_path = os.path.join('templates', 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(HTML_CONTENT)
    print(f" - [YARATILDI] {index_path}")
    
    # db_setup.py yozish
    with open('db_setup.py', 'w', encoding='utf-8') as f:
        f.write(DB_SETUP_CONTENT)
    print(" - [YARATILDI] db_setup.py")
    
    # app.py yozish
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(APP_CONTENT)
    print(" - [YARATILDI] app.py")
    
    # .env yozish (agar mavjud bo'lmasa)
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(ENV_CONTENT)
        print(" - [YARATILDI] .env (API kalitlarini sozlash uchun)")
    else:
        print(" - [MAVJUD] .env fayli allaqachon mavjud, qayta yozilmadi.")

def install_dependencies():
    """Zaruriy kutubxonalarni o'rnatish"""
    print("\n2. Kutubxonalarni o'rnatish (pip install)...")

    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        print(f" - [XATOLIK] '{requirements_file}' fayli topilmadi. Iltimos, uni yarating.")
        sys.exit(1)
        
    try:
        # Endi kutubxonalarni requirements.txt faylidan o'rnatamiz
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
        print(" - [MUVAFFAQIYATLI] Kutubxonalar o'rnatildi.")
    except Exception as e:
        print(f" - [XATOLIK] Kutubxonalarni o'rnatishda muammo bo'ldi: {str(e)}")
        sys.exit(1)

def setup_database():
    """Ma'lumotlar bazasini yaratish"""
    print("\n3. Ma'lumotlar bazasini sozlash (SQLite)...")
    try:
        subprocess.run([sys.executable, "db_setup.py"], check=True)
        print(" - [MUVAFFAQIYATLI] Ma'lumotlar bazasi sozlindi.")
    except Exception as e:
        print(f" - [XATOLIK] Baza yaratishda muammo bo'ldi: {str(e)}")
        sys.exit(1)

def run_flask_server():
    """Flask ilovasini ishga tushirish"""
    print("\n4. Flask serverini ishga tushirish...")
    print("=" * 60)
    print("Tizim ishga tushmoqda...")
    print("Saytni ko'rish uchun quyidagi manzilni brauzerda oching:")
    print("--> http://127.0.0.1:5000")
    print("Serverni o'chirish uchun terminalda CTRL + C tugmalarini bosing.")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nServer muvaffaqiyatli to'xtatildi. Xizmat ko'rsatish uchun rahmat!")

if __name__ == '__main__':
    print("=" * 60)
    print("  AQLLI KUTUBXONA TIZIMI - AVTOMATIK SOZLASH VA ISHGA TUSHIRISH")
    print("=" * 60)
    create_files()
    install_dependencies()
    setup_database()
    run_flask_server()
