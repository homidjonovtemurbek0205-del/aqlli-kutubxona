import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from core.models import User, Book

import uuid

def run_tests():
    c = Client()
    test_suffix = uuid.uuid4().hex[:6]
    test_email = f"test_{test_suffix}@library.com"
    test_username = f"user_{test_suffix}"
    print(f"1. Testing Registration Endpoint (/api/auth/register/) with {test_email}...")
    reg_resp = c.post('/api/auth/register/', {
        'email': test_email,
        'username': test_username,
        'password': 'password123'
    }, content_type='application/json', HTTP_HOST='127.0.0.1')

    print("Registration response code:", reg_resp.status_code)
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.content}"

    print("2. Testing Login Endpoint (/api/auth/login/)...")
    login_resp = c.post('/api/auth/login/', {
        'email': test_email,
        'password': 'password123'
    }, content_type='application/json', HTTP_HOST='127.0.0.1')

    print("Login response code:", login_resp.status_code)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.content}"

    data = login_resp.json()
    access_token = data['access']
    print("Access token received successfully.")

    print("3. Testing /api/auth/me/ endpoint...")
    me_resp = c.get('/api/auth/me/', HTTP_AUTHORIZATION=f'Bearer {access_token}', HTTP_HOST='127.0.0.1')
    print("Me endpoint response code:", me_resp.status_code, me_resp.json())
    assert me_resp.status_code == 200

    print("4. Testing /api/books/ endpoint...")
    books_resp = c.get('/api/books/', HTTP_AUTHORIZATION=f'Bearer {access_token}', HTTP_HOST='127.0.0.1')
    print("Books count:", len(books_resp.json()))
    assert books_resp.status_code == 200

    print("5. Testing Index View (HTML page)...")
    idx_resp = c.get('/', HTTP_HOST='127.0.0.1')
    print("Index page response code:", idx_resp.status_code)
    assert idx_resp.status_code == 200


    print("\nALL API TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()

