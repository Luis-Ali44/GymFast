from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_welcome():
    response = client.get("/")
    assert response.status_code == 200

def test_gym():
    response = client.get("/gyms")
    assert response.status_code == 200

def test_login():
    response = client.post( "/auth/login", json= {
        "email" : "admin@gymone.com",
        "password" : "qwerty123"
        }
    )
    assert response.status_code == 200