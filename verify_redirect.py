import requests
import sys

def verify_redirect():
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000'
    login_url = f'{base_url}/en/login/'
    
    # 1. Login
    print(f"1. GET {login_url}")
    response = session.get(login_url)
    csrftoken = session.cookies.get('csrftoken')
    
    print(f"2. POST {login_url} (Login)")
    payload = {
        'username': 'web_test_user',
        'password': 'password123',
        'csrfmiddlewaretoken': csrftoken
    }
    headers = {'Referer': login_url}
    
    response = session.post(login_url, data=payload, headers=headers, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        location = response.headers.get('Location')
        print(f"   Redirect Location: {location}")
        if '/profile/' in location:
            print("   SUCCESS: Login redirected to profile")
        else:
            print(f"   FAILURE: Login redirected to {location}, expected profile")
    else:
        print("   FAILURE: Login did not redirect")

    # 2. Access Login Page while Authenticated
    print(f"\n3. GET {login_url} (Authenticated)")
    response = session.get(login_url, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        location = response.headers.get('Location')
        print(f"   Redirect Location: {location}")
        if '/profile/' in location:
            print("   SUCCESS: Authenticated access redirected to profile")
        else:
            print(f"   FAILURE: Authenticated access redirected to {location}, expected profile")
    else:
        print("   FAILURE: Authenticated access did not redirect (likely 200 OK)")

if __name__ == '__main__':
    verify_redirect()
