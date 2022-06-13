import os, re, random, json, secrets
from urllib.request import urlopen
from urllib import request, parse
import bcrypt

import database as db

from fastapi import FastAPI, HTTPException, Form, Request

app = FastAPI()
email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+") # <account>@<host>.<tld>

def send_code(email: str):
    code = random.randint(0, 9999)
    try:
        data = parse.urlencode({'to': email, 'subject': 'Your new code', 'body': str(code)}).encode()
        with urlopen(os.getenv("SMTP_HTTP_API","http://127.0.0.1:8025")+"/send", data=data) as response:
            response_content = response.read()
            if not json.loads(response_content):
                return {'ok': False, 'reason': 'Something went wrong while tring to send your activation code'}
            db.create_activation(email, str(code))
    except db.PendingActivationCodeException:
        return {'ok': False, 'reason': 'You are already registered but you need to activate your account'}
    except:
        raise HTTPException(status_code=500, detail="Cannot send your new registration code")

@app.post("/register")
def register(email: str = Form(), password: str = Form()):
    # check email
    if not email_regex.match(email):
        return {'ok': False, 'reason': 'Your email is miswritten'}
    # check password strength, at least a min length
    if len(password)<5 or len(password)>32: #BCrypt has a limit of 72 chars, so we define an acceptable length
        return {'ok': False, 'reason': 'Password is too short or too long (5 to 32 characters are required)'}
    if db.get_user(email):
        return {'ok': False, 'reason': 'You are already registered'}
    hashed = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt(12))
    db.create_user(email, hashed.decode())
    send_code(email)
    return {'ok': True}

@app.post("/login")
def login(email: str = Form(), password: str = Form()):
    """ Log the user in
    For security reason, we do not differentiate wrong email and wrong password if the auth fails
    """
    u=db.get_user(email)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if bcrypt.checkpw(password.encode('UTF-8'), u[2].encode('UTF-8')):
        a=db.auth(u[0], secrets.token_urlsafe(64))
        return {'token':a[1], 'expires': a[2]}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/validate")
def validate(email: str = Form(), code: str = Form()):
    try:
        db.activate_user(email, code)
    except db.ExpiredActivationCodeException:
        return {'ok': False, 'reason': 'Registration code has expired, you need to resend it'}
    except db.WrongActivationCodeException:
        return {'ok': False, 'reason': 'Your registration code is wrong'}
    return {'ok': True}
