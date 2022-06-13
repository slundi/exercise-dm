import os, time
import psycopg2

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)
conn = psycopg2.connect(host=os.getenv("POSTGRES_HOST","localhost"), dbname=os.getenv("POSTGRES_DB","postgres"), user=os.getenv("POSTGRES_USER","postgres"), password=os.getenv("POSTGRES_PASSWORD"))
cur = conn.cursor()

def test_registration_email():
    response = client.post("/register", data={'email': 'wrong-email', 'password': 'password1'})
    assert response.status_code == 200
    assert response.json() == {'ok': False, 'reason': 'Your email is miswritten'}

def test_registration_passwords():
    # too short
    response = client.post("/register", data={'email': 'test_wp1@test.tld', 'password': '0'})
    assert response.status_code == 200
    assert response.json() == {'ok': False, 'reason': 'Password is too short or too long (5 to 32 characters are required)'}
    # too long
    response = client.post("/register", data={'email': 'test_wp2@test.tld', 'password': 'password'*8})
    assert response.status_code == 200
    assert response.json() == {'ok': False, 'reason': 'Password is too short or too long (5 to 32 characters are required)'}

# This part requires the SMTP server to work
def test_register_user():
    cur.execute("DELETE FROM users")
    conn.commit()
    response = client.post("/register", data={'email': 'test_register_ok@test.ts', 'password': 'password1'})
    assert response.status_code == 200
    assert response.json() == {'ok': True}

def test_register_user_doubles():
    cur.execute("DELETE FROM users")
    conn.commit()
    response = client.post("/register", data={'email': 'test_register_double@test.ts', 'password': 'password1'})
    assert response.status_code == 200
    assert response.json() == {'ok': True}

    response = client.post("/register", data={'email': 'test_register_double@test.ts', 'password': 'password1'})
    assert response.status_code == 200
    assert response.json() == {'ok': False, 'reason': 'You are already registered'} or response.json() == {'ok': False, 'reason': 'You are already registered but you need to activate your account'}


def test_validate_user():
    cur.execute("DELETE FROM activation_codes")
    cur.execute("DELETE FROM users")
    conn.commit()
    #validate user with valid delay
    cur.execute("INSERT INTO users (id, email, psw) VALUES (%(id)s, %(e)s, %(p)s)", {'id': 65535, 'e': 'validate1@test.ts', 'p': 'dummy-password'})
    cur.execute("INSERT INTO activation_codes (user_id, code, expires) VALUES(%(u)s, %(c)s, NOW() AT TIME ZONE('utc') + 60 * interval '1 second')", {'u': 65535, 'c': 1234})
    conn.commit()
    time.sleep(1)
    #test a wrong code first
    response = client.post("/validate", data={'email': 'validate1@test.ts', 'code': '1111'})
    assert response.status_code == 200
    assert response.json() == {'ok': False, 'reason': 'Your registration code is wrong'}
    #test good code then
    response = client.post("/validate", data={'email': 'validate1@test.ts', 'code': '1234'})
    assert response.status_code == 200
    assert response.json() == {'ok': True}

    #do not validate user with invalid delay
    cur.execute("INSERT INTO users (id, email, psw) VALUES (%(id)s, %(e)s, %(p)s)", {'id': 65536, 'e': 'validate2@test.ts', 'p': 'dummy-password'})
    cur.execute("INSERT INTO activation_codes (user_id, code, expires) VALUES(%(u)s, %(c)s, NOW() AT TIME ZONE('utc') - 60 * interval '1 second')", {'u': 65536, 'c': 5678})
    conn.commit()
    time.sleep(1)
    response = client.post("/validate", data={'email': 'validate2@test.ts', 'code': '1234'})
    assert response.status_code == 200
    assert response.json() == {'ok': False, 'reason': 'Registration code has expired, you need to resend it'}

def test_login():
    cur.execute("DELETE FROM users")
    conn.commit()
    response = client.post("/register", data={'email': 'test_1@test.ts', 'password': 'password1'})
    response = client.post("/login", data={'email': 'test_1@test.ts', 'password': 'wrong-password'})
    assert response.status_code == 401

    response = client.post("/login", data={'email': 'test_dos_not_exists@test.ts', 'password': 'does-not-exists'})
    assert response.status_code == 401

    response = client.post("/login", data={'email': 'test_1@test.ts', 'password': 'password1'})
    assert response.status_code == 200
    result = response.json().keys()
    assert 'token' in result and 'expires' in result
