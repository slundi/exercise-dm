import os

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_smtp_server():
    os.environ["FROM_EMAIL"] = "test@test.test"
    # check OK email
    response = client.post("/send", data={'to': 'check@test.ts', 'subject': 'test subject', 'body': 'sample text'})
    assert response.status_code == 200
    assert response.json() == True

    # check wrong email
    response = client.post("/send", data={'to': 'wrong-email', 'subject': 'test subject', 'body': 'sample text'})
    assert response.status_code == 400

