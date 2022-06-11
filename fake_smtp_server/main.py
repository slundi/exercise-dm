import os, re

from fastapi import FastAPI, HTTPException

app = FastAPI()
email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+") # <account>@<host>.<tld>

@app.get("/send")
def send_email(to: str, subject: str, body: str):
    if not email_regex.match(to):
        raise HTTPException(status_code=400, detail="Invalid email target")
    print("Sending email\n\t\tFrom:   ", os.getenv("from_email"),"\n\t\tTo:     ", to,"\n\t\tSubject:",subject,"\n\t\tBody:   ", body)
    return True
