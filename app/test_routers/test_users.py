import uuid


class TestCreateUser:
    """POST /users/"""

    def test_create_user_success(self, client, mocker):
        mock_send_email = mocker.patch("app.routers.users.send_verification_email")
        data = {
            "username": "user0",
            "email": "test1@example.com",
            "password": "testing",
        }
        response = client.post("/users", json=data)
        mock_send_email.assert_called_once()
        assert response.status_code == 201
        assert response.json()["username"] == data["username"]
        assert response.json()["email"] == data["email"]
        assert response.json()["role"] == 1
        assert response.json()["password"] != data["password"]

    def test_create_user_missing_fields(self, client, mocker):
        mock_send_email = mocker.patch("app.routers.users.send_verification_email")
        incomplete_data = {"username": "testuser"}
        response = client.post("/users/", json=incomplete_data)
        assert response.status_code == 422
        mock_send_email.assert_not_called()


class TestLogin:
    """POST /auth/login"""

    def test_login_success(self, client, create_user):
        login_data = {"username": create_user["username"], "password": "password123"}
        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
        assert len(response.json()["access_token"]) > 0

    def test_login_user_not_found(self, client):
        login_data = {"username": "nonexistentuser", "password": "anypassword"}
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == 404

    def test_login_wrong_password(self, client, create_user):
        login_data = {"username": create_user["username"], "password": "wrongpassword"}
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == 400


class TestGetCurrentUser:
    """GET /users/me"""

    def test_get_current_user_success(self, client, login_user):
        response = client.get(
            "/users/me", headers={"Authorization": f"Bearer {login_user['token']}"}
        )
        user = login_user["user"]
        user_data = response.json()
        assert response.status_code == 200
        assert user_data["username"] == user["username"]
        assert user_data["email"] == user["email"]

        assert "id" in user_data
        assert "username" in user_data
        assert "email" in user_data
        assert "role" in user_data
        assert "created_at" in user_data
        assert "password" not in user_data

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/users/me")
        assert response.status_code in [401, 403]

    def test_get_current_user_invalid_token(self, client):
        response = client.get(
            "/users/me", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 400


class TestUpdateUsername:
    """PATCH /users/me/change_username"""

    def test_update_username_success(self, client, login_user):
        token = login_user["token"]

        update_data = {"username": "new_username"}
        response = client.patch(
            "/users/me/change_username",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        me_response = client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.json()["username"] == "new_username"

    def test_update_username_unauthorized(self, client):
        update_data = {"username": "new_username"}
        response = client.patch("/users/me/change_username", json=update_data)
        assert response.status_code in [401, 403]


class TestUpdateEmail:
    """PATCH /users/me/change_email"""

    def test_update_email_success(self, client, login_user):
        token = login_user["token"]
        update_data = {"email": "new@example.com"}
        response = client.patch(
            "/users/me/change_email",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 202

    def test_update_email_invalid_format(self, client, login_user):
        token = login_user["token"]
        update_data = {"email": "invalid-email"}
        response = client.patch(
            "/users/me/change_email",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    def test_update_email_unauthorized(self, client):
        update_data = {"email": "new@example.com"}
        response = client.patch("/users/me/change_email", json=update_data)
        assert response.status_code in [401, 403]

    def test_update_email_same_email(self, client, login_user):
        update_data = {"email": "test@example.com"}
        response = client.patch(
            "/users/me/change_email",
            json=update_data,
            headers={"Authorization": f"Bearer {login_user['token']}"},
        )
        assert response.status_code == 400

    def test_update_email_duplicate(self, client, login_user, create_user):
        update_data = {"email": "other@example.com"}
        response = client.patch(
            "/users/me/change_email",
            json=update_data,
            headers={"Authorization": f"Bearer {login_user['token']}"},
        )
        assert response.status_code == 409


class TestUpdatePassword:
    """PATCH /users/me/change_password"""

    def test_update_password_success(self, client, login_user):
        user = login_user["user"]
        update_data = {
            "old_password": "securepassword123",
            "new_password": "newsecurepassword456",
        }
        response = client.patch(
            "/users/me/change_password",
            json=update_data,
            headers={"Authorization": f"Bearer {login_user['token']}"},
        )
        assert response.status_code == 200

        old_login_response = client.post(
            "/auth/login",
            data={"username": user["username"], "password": "securepassword123"},
        )
        assert old_login_response.status_code == 400

        new_login_response = client.post(
            "/auth/login",
            data={"username": user["username"], "password": "newsecurepassword456"},
        )
        assert new_login_response.status_code == 200
        assert "access_token" in new_login_response.json()

    def test_update_password_wrong_old_password(self, client, login_user):
        update_data = {
            "old_password": "wrongpassword",
            "new_password": "newsecurepassword456",
        }
        response = client.patch(
            "/users/me/change_password",
            json=update_data,
            headers={"Authorization": f"Bearer {login_user['token']}"},
        )
        assert response.status_code == 400

    def test_update_password_unauthorized(self, client):
        update_data = {
            "old_password": "securepassword123",
            "new_password": "newsecurepassword456",
        }
        response = client.patch("/users/me/change_password", json=update_data)
        assert response.status_code == 403


class TestDeleteUser:
    """DELETE /users/me"""

    def test_delete_user_success(self, client, login_user):
        response = client.delete(
            "/users/me", headers={"Authorization": f"Bearer {login_user['token']}"}
        )
        assert response.status_code == 200

        me_response = client.get(
            "/users/me", headers={"Authorization": f"Bearer {login_user['token']}"}
        )
        assert me_response.status_code == 400

        login_response = client.post(
            "/auth/login",
            data={
                "username": login_user["user"]["username"],
                "password": login_user["user"]["password"],
            },
        )
        assert login_response.status_code == 404

    def test_delete_user_unauthorized(self, client):
        response = client.delete("/users/me")
        assert response.status_code == 403


class TestGetUserById:
    """GET /users/{user_id}"""

    def test_get_user_by_id_success(self, client, login_user, create_user):
        user_id = create_user["id"]
        response = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {login_user['token']}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(user_id)
        assert response.json()["username"] == create_user["username"]
        assert response.json()["email"] == create_user["email"]

    def test_get_user_by_id_not_found(self, client, login_user):
        non_existent_id = uuid.uuid4()
        response = client.get(
            f"/users/{non_existent_id}",
            headers={"Authorization": f"Bearer {login_user['token']}"},
        )
        assert response.status_code == 404

    def test_get_user_by_id_invalid_uuid(self, client, login_user):
        response = client.get(
            "/users/invalid-uuid",
            headers={"Authorization": f"Bearer {login_user['token']}"},
        )
        assert response.status_code == 422

    def test_get_user_by_id_unauthorized(self, client, login_user):
        user_id = login_user["user"]["id"]
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 403
