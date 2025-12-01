import requests
import sys

def debug_admin_login():
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000'
    login_url = f'{base_url}/en/admin/login/'
    
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
        'username': 'admin',
        'password': 'adminpassword123',
        'csrfmiddlewaretoken': csrftoken,
        'next': '/en/admin/'
    }
    headers = {
        'Referer': login_url
    }
    
    response = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    print(f"   Status: {response.status_code}")
    # 3. Get Home Page to find Admin Link
    print("\n3. GET Home Page")
    home_url = f'{base_url}/en/'
    response = session.get(home_url)
    print(f"   Status: {response.status_code}")
    
    if 'href="/en/admin/"' in response.text or "href='/en/admin/'" in response.text:
        print("   SUCCESS: Admin link found with correct URL (/en/admin/)")
        # Optional: Follow it to be sure
        admin_url = f'{base_url}/en/admin/'
        response = session.get(admin_url)
        if "Site administration" in response.text or "網站管理" in response.text:
             print("   SUCCESS: Admin link leads to dashboard")
        else:
             print("   FAILURE: Admin link does not lead to dashboard")
    else:
        print("   FAILURE: Admin link not found or incorrect URL")
        # Print some context around "Admin" text
        try:
            idx = response.text.index("Admin")
            print(f"   Context: {response.text[idx-50:idx+50]}")
        except ValueError:
            print("   'Admin' text not found in response")

if __name__ == '__main__':
    debug_admin_login()
