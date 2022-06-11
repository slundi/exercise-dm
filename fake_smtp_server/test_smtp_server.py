import os

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)
os.environ["FROM_EMAIL"] = "test@test.test"

def test_email_ok():
    response = client.post("/send", data={'to': 'check@test.ts', 'subject': 'test subject', 'body': 'sample text'})
    assert response.status_code == 200
    assert response.json() == True

def test_wrong_email():
    response = client.post("/send", data={'to': 'wrong-email', 'subject': 'test subject', 'body': 'sample text'})
    assert response.status_code == 400
