def test_create_user(client):
    data = {
        "username": "user0",
        "email": "testuser@nofoobar.com",
        "password": "testing",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 201
    assert response.json()["username"] == data["username"]
    assert response.json()["email"] == data["email"]
    assert response.json()["role"] == 1
    assert response.json()["password"] != data["password"]
