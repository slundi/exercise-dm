import os, re

from fastapi import FastAPI, HTTPException, Form

app = FastAPI()
email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+") # <account>@<host>.<tld>

@app.post("/send")
def send_email(to: str = Form(), subject: str = Form(), body: str = Form()):
    if not email_regex.match(to):
        raise HTTPException(status_code=400, detail="Invalid email target")
    print("Sending email\n\t\tFrom:   ", os.getenv("FROM_EMAIL"),"\n\t\tTo:     ", to,"\n\t\tSubject:",subject,"\n\t\tBody:   ", body)
    return True
