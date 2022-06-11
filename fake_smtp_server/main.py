import os
from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/send")
def send_email(to: str, subject: str, body: str):
    print("Sending email\n\t\tFrom:\t", os.getenv("from_email"),"\n\t\tTo:\t", to,"\n\t\tSubject:\t",subject,"\n\t\tBody:\t:", body)
    return True
