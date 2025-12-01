import requests
import sys

def debug_login():
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000'
    login_url = f'{base_url}/en/login/'
    
    print(f"1. GET {login_url}")
    response = session.get(login_url)
    print(f"   Status: {response.status_code}")
    csrftoken = session.cookies.get('csrftoken')
    print(f"   CSRF Token: {csrftoken}")
    
    if not csrftoken:
        print("   ERROR: No CSRF token found")
        return

    print(f"2. POST {login_url}")
    payload = {
        'username': 'web_test_user',
        'password': 'password123',
        'csrfmiddlewaretoken': csrftoken
    }
    headers = {
        'Referer': login_url
    }
    
    response = session.post(login_url, data=payload, headers=headers, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {response.headers}")
    print(f"   Content (first 500 chars): {response.text[:500]}")
    
    if response.status_code == 302:
        print(f"   Redirect Location: {response.headers.get('Location')}")
    else:
        print("   NOT REDIRECTED")

    print("\n3. POST {login_url} (Invalid Credentials)")
    payload_invalid = {
        'username': 'web_test_user',
        'password': 'wrongpassword',
        'csrfmiddlewaretoken': csrftoken
    }
    response = session.post(login_url, data=payload_invalid, headers=headers, allow_redirects=False)
    print(f"   Status: {response.status_code}")

if __name__ == '__main__':
    debug_login()
