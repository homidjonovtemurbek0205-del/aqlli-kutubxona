# Implementation Plan - Modern Library Frontend, Audio Book Support & Permission Fixes

Fix all issues in the Aqlli Kutubxona codebase, implement comprehensive audio book support for books, restrict book deletion and addition (books & audiobooks) exclusively to admins, and deliver a modern, high-performance responsive frontend.

---

## User Review Required

> [!IMPORTANT]
> **Key Architectural & Permission Rules**:
> 1. **Only Admins** can delete books (`DELETE /api/books/<id>/`).
> 2. **Only Admins** can add books and upload/attach audio books (`POST /api/books/`, `POST /api/books/<id>/upload-audio/`, `POST /api/upload-pdf/`, `POST /api/upload-zip/`).
> 3. **Regular Users and Readers** can browse books, read PDFs, listen to audio books using the modern audio player, and chat with the AI librarian, but cannot delete or add books.
> 4. We will add an `audio_file` field to the `Book` model and provide a seamless bottom audio player bar with play/pause, seekbar, speed control (1x, 1.25x, 1.5x, 2x), and time formatting.
> 5. We will ensure default credentials exist for easy testing:
>    - **Admin**: `admin@library.com` / `admin123`
>    - **User**: `user@library.com` / `user123`
> 6. We will populate existing 46 PDF books from `media/books/` into the database so the library is immediately rich with real content.

---

## Code Issues Identified & Solutions

1. **`test_gemini.py` Crash during Django Test Discovery**:
   - *Problem*: `test_gemini.py` imports deprecated `google.generativeai` which crashes on Python 3.14 with `TypeError: Metaclasses with custom tp_new are not supported.`.
   - *Fix*: Update `test_gemini.py` to use modern `from google import genai` (`google-genai` library), matching `core/views.py`.
2. **AI Chatbot Broken in Frontend**:
   - *Problem*: `core/templates/core/index.html` calls `sendMessage()`, but the function was named `sendChatMessage()`, causing an unhandled JS ReferenceError when submitting chat messages.
   - *Fix*: Fix function name and integrate smooth message streaming/bubbles and quick prompt chips.
3. **Outdated `requirements.txt`**:
   - *Problem*: `requirements.txt` only listed Flask dependencies and lacked Django, Django REST Framework, SimpleJWT, django-cors-headers, and google-genai.
   - *Fix*: Update `requirements.txt` with complete, modern dependencies.
4. **Outdated `run_project.py`**:
   - *Problem*: `run_project.py` attempted to launch the legacy Flask `app.py` on `library.db` instead of the Django REST application.
   - *Fix*: Update `run_project.py` to run Django migrations, ensure seed admin/user and books exist, and start `python manage.py runserver`.
5. **No Audio Book Support in Backend**:
   - *Problem*: `Book` model had no `audio_file` field. No serializer or API endpoints existed to handle audio files.
   - *Fix*: Add `audio_file = models.FileField(upload_to='audio/', null=True, blank=True)` to `Book`, update `BookSerializer` to handle file URLs and audio uploads, and add `@action(detail=True, methods=['post'])` endpoint `upload_audio` on `BookViewSet`.
6. **Admin-Only Permissions for Book & Audio Addition and Deletion**:
   - *Problem*: Need strict verification that only admin (`is_staff` or `is_superuser`) can delete books or add/modify books and audio books.
   - *Fix*: Enforce permissions in `BookViewSet` (`IsAdminOrReadOnly`), PDF/ZIP upload views, and the new audio upload view.
7. **Empty Database**:
   - *Problem*: 46 PDF books exist in `media/books/`, but `db.sqlite3` had 0 books and 0 admin users.
   - *Fix*: Create a management command `populate_books` to seed books and ensure the admin user is created.

---

## Proposed Changes

### Backend & Database Layer

#### [MODIFY] [core/models.py](file:///C:/Users/Surface%20PC/.gemini/core/models.py)
- Add `audio_file = models.FileField(upload_to='audio/', null=True, blank=True, verbose_name="Audio kitob fayli")` to `Book` model.
- Add `has_audio` helper property.

#### [NEW] [core/migrations/0002_book_audio_file.py](file:///C:/Users/Surface%20PC/.gemini/core/migrations/0002_book_audio_file.py)
- Migration generated via `makemigrations` to add `audio_file` to `Book`.

#### [MODIFY] [core/serializers.py](file:///C:/Users/Surface%20PC/.gemini/core/serializers.py)
- Include `audio_file` in `BookSerializer.Meta.fields`.
- Handle absolute URL resolution for `audio_file` in `to_representation`.
- Add `AudioUploadSerializer` for validating audio file uploads (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.aac`).

#### [MODIFY] [core/views.py](file:///C:/Users/Surface%20PC/.gemini/core/views.py)
- In `BookViewSet`:
  - Add `parser_classes = (MultiPartParser, FormParser, JSONParser)`.
  - Add `@action(detail=True, methods=['post'], permission_classes=[IsAdminUser], parser_classes=[MultiPartParser, FormParser])` for `upload_audio`.
  - Ensure delete and create operations strictly require admin privileges.
- In `AIChatView`:
  - Enhance fallback responses and error resilience.

#### [NEW] [core/management/commands/setup_library.py](file:///C:/Users/Surface%20PC/.gemini/core/management/commands/setup_library.py)
- Seed default admin user (`admin@library.com` / `admin123`) and test user (`user@library.com` / `user123`).
- Scan `media/books/` and automatically register all existing PDF books in `db.sqlite3` with titles and descriptions.

---

### Modern Frontend Experience

#### [MODIFY] [core/templates/core/index.html](file:///C:/Users/Surface%20PC/.gemini/core/templates/core/index.html)
Redesign and upgrade the interface with:
1. **Modern Aesthetic**:
   - Deep cyber-glass dark theme with violet & teal glowing accents.
   - Fluid typography and responsive layout.
2. **Top Navigation & Controls**:
   - Brand logo, live search bar (instant filter by title, author, genre).
   - Category filter pills (Barchasi, Badiiy, Psixologiya, Roman, Diniy, Tarixiy, etc.).
   - User profile badge with clear role indicator (`Admin` badge with crown vs `Kitobxon` badge).
   - Admin action toolbar: "Yangi Kitob Qo'shish" button, PDF upload, ZIP upload.
   - Clean logout & login/register toggles.
3. **Hero Dashboard Stats**:
   - Total Books count, Audio Books count, Categories count, AI status.
4. **Enhanced Book Cards**:
   - Stylized book card with genre badge, title, author, description preview.
   - Status indicators: `[PDF]` and `[🎧 Audio]` badge if an audio book is attached.
   - Action buttons:
     - 📖 **O'qish (Read)**: Opens reader modal with PDF frame & extracted text.
     - 🎧 **Tinglash (Listen)**:
       - If `audio_file` exists: launches the floating audio player bar and starts playing the actual audio book.
       - If no `audio_file`: uses browser text-to-speech with clear notice.
     - 🎵 **Audio biriktirish (Add Audio Book)**: **Admin only**. Allows uploading an audio file specifically for this book.
     - 🗑️ **O'chirish (Delete)**: **Admin only**. Prompts confirmation dialog and deletes book via API.
5. **Modern Persistent Audio Player**:
   - Floating bottom player bar with Play/Pause, 10s Skip/Back, interactive seekbar, elapsed/total time, volume slider, playback rate switcher (0.75x, 1x, 1.25x, 1.5x, 2x), and dismiss button.
6. **Admin Modals**:
   - **"Yangi Kitob Qo'shish" Modal**: Form with Title, Author, Genre, Description, PDF file input, and Audio Book file input.
   - **"Audio Kitob Yuklash" Modal**: Quick audio upload for an existing book.
7. **AI Librarian Chat Widget**:
   - Fix `sendMessage` function.
   - Quick prompt suggestion chips.
   - Auto-scrolling chat history with formatting.
8. **Toast Alert System**:
   - Non-blocking notification toasts (Success, Error, Info) replacing browser alerts.

---

### Scripts & Project Configuration

#### [MODIFY] [test_gemini.py](file:///C:/Users/Surface%20PC/.gemini/test_gemini.py)
- Use `from google import genai` to prevent Python 3.14 protobuf crash.

#### [MODIFY] [requirements.txt](file:///C:/Users/Surface%20PC/.gemini/requirements.txt)
- Add Django, djangorestframework, djangorestframework-simplejwt, django-cors-headers, google-genai, pymupdf, pypdf, etc.

#### [MODIFY] [run_project.py](file:///C:/Users/Surface%20PC/.gemini/run_project.py)
- Run Django migrations, run `setup_library` to ensure admin and books exist, and launch Django development server.

#### [MODIFY] [core/tests.py](file:///C:/Users/Surface%20PC/.gemini/core/tests.py)
- Add tests for:
  - Admin adding book with audio file.
  - Admin uploading audio to an existing book (`/api/books/<id>/upload-audio/`).
  - Regular user forbidden from adding books or audio (403 Forbidden).
  - Admin deleting book (204 No Content).
  - Regular user forbidden from deleting books (403 Forbidden).

---

## Verification Plan

### Automated Tests
1. Run Django test suite:
   ```powershell
   .\venv\Scripts\python.exe manage.py test core
   ```
   Must pass all existing and new unit tests (auth, permissions, PDF extraction, ZIP upload, audio upload, deletion permissions).
2. Run `test_api.py`:
   ```powershell
   .\venv\Scripts\python.exe test_api.py
   ```
   Verify registration, login, token auth, `/api/auth/me/`, `/api/books/`, and index view.

### Manual Verification
1. Launch Django server:
   ```powershell
   .\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
   ```
2. Log in as regular user (`user@library.com`):
   - Confirm book deletion buttons and admin upload options are hidden.
   - Confirm attempting to delete or upload returns 403 Forbidden.
   - Test "O'qish" (reader modal) and "Tinglash" (audio player / text-to-speech).
   - Test AI Chat widget with a prompt.
3. Log in as admin (`admin@library.com`):
   - Confirm admin badges, "Yangi Kitob Qo'shish" button, PDF/ZIP cards, "+ Audio" button, and Delete button are visible.
   - Test adding a new book with both PDF and Audio file.
   - Test attaching an audio file to an existing book.
   - Test playing the uploaded audio file in the modern player.
   - Test deleting a book.
