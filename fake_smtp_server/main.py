import os
from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/send")
def send_email(to: str, subject: str, body: str):
    print("Sending email\n\t\tFrom:   ", os.getenv("from_email"),"\n\t\tTo:     ", to,"\n\t\tSubject:",subject,"\n\t\tBody:   ", body)
    return True
