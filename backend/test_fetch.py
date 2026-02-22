import requests, json

r = requests.post('http://localhost:8000/api/auth/login', json={'username':'admin','password':'password'})
print("Login status:", r.status_code)
if r.status_code == 200:
    t = r.json().get('access_token')
    res = requests.get('http://localhost:8000/api/assets', headers={'Authorization': f'Bearer {t}'})
    print("Assets status:", res.status_code)
    try:
        print("Response:", json.dumps(res.json(), indent=2)[:500])
    except:
        print("Raw response:", res.text[:500])
else:
    print("Failed to authenticate.")
