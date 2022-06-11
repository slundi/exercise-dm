import os, re, random, json
from urllib.request import urlopen
import bcrypt

import database

from fastapi import FastAPI, HTTPException

app = FastAPI()
email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+") # <account>@<host>.<tld>

@app.get("/register")
def register(email: str, password: str):
    # check email
    if not email_regex.match(email):
        return {'ok': False, 'reason': 'Your is miswritten'}
    # check password strength, at least a min length
    if len(password)<5:
        return {'ok': False, 'reason': 'Password is too short (5 characters minimum are required)'}
    #TODO: check email is unique in DB
    if True:
        return {'ok': False, 'reason': 'You are already registered'}
    #TODO: insert in DB
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(16))
    return {'ok': True}

@app.get("/login")
def login(email: str, password: str):
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(16))
    if bcrypt.checkpw(password, hashed):
        print("It Matches!")
        #TODO: session if auth OK
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return True

@app.get("/validate")
def validate(email: str, code: int):
    #TODO: check valid datetime with timezone
    if True:
        return {'ok': False, 'reason': 'Registration code has expired, you need to resend it'}
    #TODO: check valid code
    if True:
        return {'ok': False, 'reason': 'Your registration code is wrong'}
    return {'ok': True}

@app.get("/resend-code")
def resend_code(email: str):
    #TODO: check if a valid code is active
    if True:
        return {'ok': False, 'reason': 'A registration code is already active or please wait TODO to ask for a new one'}
    #TODO begin transaction because if we can't send the email, we should not block the client
    code = random.randint(0, 9999)
    try:
        with urlopen("http://fake_smtp_server:8025/send?to=email&subject=Your+new+code&body="+str(code)) as response:
            response_content = response.read()
        if not json.load(response_content):
            return {'ok': False, 'reason': 'Something went wrong while tring to send your activation code'}
    except:
        raise HTTPException(status_code=500, detail="Cannot send your new registration code")
    #commit if OK
    return {'ok': True}
