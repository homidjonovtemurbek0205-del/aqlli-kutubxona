import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from core.models import User, Book

def run_tests():
    c = Client()
    print("1. Testing Registration Endpoint (/api/auth/register/)...")
    reg_resp = c.post('/api/auth/register/', {
        'email': 'newtestuser@library.com',
        'username': 'newtestuser',
        'password': 'password123'
    }, content_type='application/json')
    print("Registration response code:", reg_resp.status_code)
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.content}"

    print("2. Testing Login Endpoint (/api/auth/login/)...")
    login_resp = c.post('/api/auth/login/', {
        'email': 'newtestuser@library.com',
        'password': 'password123'
    }, content_type='application/json')
    print("Login response code:", login_resp.status_code)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.content}"

    data = login_resp.json()
    access_token = data['access']
    print("Access token received successfully.")

    print("3. Testing /api/auth/me/ endpoint...")
    me_resp = c.get('/api/auth/me/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
    print("Me endpoint response code:", me_resp.status_code, me_resp.json())
    assert me_resp.status_code == 200

    print("4. Testing /api/books/ endpoint...")
    books_resp = c.get('/api/books/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
    print("Books count:", len(books_resp.json()))
    assert books_resp.status_code == 200

    print("5. Testing Index View (HTML page)...")
    idx_resp = c.get('/')
    print("Index page response code:", idx_resp.status_code)
    assert idx_resp.status_code == 200

    print("\nALL API TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == '__main__':
    run_tests()
