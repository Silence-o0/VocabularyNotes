import uuid

import pytest

from app.exceptions import NotFoundError
from app.services import users as user_service


class TestCreateUser:
    """POST /users/"""

    def test_create_user_success(
        self, client, db_session, mock_send_verification_email
    ):
        data = {
            "username": "user0",
            "email": "test1@example.com",
            "password": "testing",
        }

        response = client.post("/users", json=data)
        assert response.status_code == 201
        mock_send_verification_email.assert_called_once()

        created_user = user_service.get_user_by_email(data["email"], db_session)
        expected_data = {
            "id": str(created_user.id),
            "username": created_user.username,
            "email": created_user.email,
            "role": created_user.role,
            "created_at": created_user.created_at.isoformat(),
        }
        assert response.json() == expected_data
        assert created_user.password != data["password"]

    def test_create_user_missing_fields(self, client, mock_send_verification_email):
        incomplete_data = {"username": "testuser"}
        response = client.post("/users/", json=incomplete_data)
        assert response.status_code == 422
        mock_send_verification_email.assert_not_called()


class TestLogin:
    """POST /auth/login"""

    def test_login_success(self, client, created_user):
        login_data = {
            "username": created_user.username,
            "password": "securepassword123",
        }
        response = client.post("/auth/login", json=login_data)

        token_data = response.json()
        assert token_data["token_type"] == "bearer"
        assert len(token_data["access_token"]) > 0

    def test_login_user_not_found(self, client):
        login_data = {"username": "nonexistentuser", "password": "anypassword"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 404

    def test_login_wrong_password(self, client, created_user):
        login_data = {"username": created_user.username, "password": "wrongpassword"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 400


class TestGetCurrentUser:
    """GET /users/me"""

    def test_get_current_user_success(self, authorized_client, created_user, db_session):
        response = authorized_client.get("/users/me")
        assert response.status_code == 200

        user_from_db = user_service.get_user_by_id(created_user.id, db_session)
        expected_data = {
            "id": str(user_from_db.id),
            "username": user_from_db.username,
            "email": user_from_db.email,
            "role": user_from_db.role,
            "created_at": user_from_db.created_at.isoformat(),
        }
        assert response.json() == expected_data

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/users/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client):
        response = client.get(
            "/users/me", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 400


class TestUpdateUsername:
    """PATCH /users/me/change_username"""

    def test_update_username_success(self, authorized_client, created_user, db_session):
        update_data = {"username": "new_username"}
        response = authorized_client.patch("/users/me/change_username", json=update_data)
        assert response.status_code == 200

        updated_user = user_service.get_user_by_id(
            created_user.id, db_session
        )
        assert updated_user.username == "new_username"

    def test_update_username_unauthorized(self, client):
        update_data = {"username": "new_username"}
        response = client.patch("/users/me/change_username", json=update_data)
        assert response.status_code == 403


class TestUpdateEmail:
    """PATCH /users/me/change_email"""

    def test_update_email_success(
        self, authorized_client, mock_send_verification_email
    ):
        update_data = {"email": "new@example.com"}
        response = authorized_client.patch("/users/me/change_email", json=update_data)
        assert response.status_code == 202
        mock_send_verification_email.assert_called_once()

    def test_update_email_invalid_format(self, authorized_client):
        update_data = {"email": "invalid-email"}
        response = authorized_client.patch("/users/me/change_email", json=update_data)
        assert response.status_code == 422

    def test_update_email_unauthorized(self, client):
        update_data = {"email": "new@example.com"}
        response = client.patch("/users/me/change_email", json=update_data)
        assert response.status_code == 403

    def test_update_email_same_email(self, authorized_client):
        update_data = {"email": "test@example.com"}
        response = authorized_client.patch("/users/me/change_email", json=update_data)
        assert response.status_code == 400

    def test_update_email_duplicate(self, authorized_client, created_another_user):
        update_data = {"email": created_another_user.email}
        response = authorized_client.patch("/users/me/change_email", json=update_data)
        assert response.status_code == 409


class TestUpdatePassword:
    """PATCH /users/me/change_password"""

    def test_update_password_success(self, authorized_client, created_user, db_session):
        update_data = {
            "old_password": "securepassword123",
            "new_password": "newsecurepassword456",
        }
        response = authorized_client.patch("/users/me/change_password", json=update_data)
        assert response.status_code == 200

        updated_user = user_service.get_user_by_id(created_user.id, db_session)
        assert updated_user.verify_password(update_data["new_password"])

    def test_update_password_wrong_old_password(self, authorized_client):
        update_data = {
            "old_password": "wrongpassword",
            "new_password": "newsecurepassword456",
        }
        response = authorized_client.patch("/users/me/change_password", json=update_data)
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

    def test_delete_user_success(self, authorized_client, created_user, db_session):
        response = authorized_client.delete("/users/me")
        assert response.status_code == 200
        with pytest.raises(NotFoundError):
            user_service.get_user_by_id(created_user.id, db_session)

    def test_delete_user_unauthorized(self, client):
        response = client.delete("/users/me")
        assert response.status_code == 403


class TestGetUserById:
    """GET /users/{user_id}"""

    def test_get_user_by_id_success(self, authorized_client, created_another_user):
        response = authorized_client.get(f"/users/{created_another_user.id}")
        assert response.status_code == 200
        assert response.json() == {
            "id": str(created_another_user.id),
            "username": created_another_user.username,
            "email": created_another_user.email,
            "role": created_another_user.role,
            "created_at": created_another_user.created_at.isoformat(),
        }

    def test_get_user_by_id_not_found(self, authorized_client):
        non_existent_id = uuid.uuid4()
        response = authorized_client.get(f"/users/{non_existent_id}")
        assert response.status_code == 404

    def test_get_user_by_id_invalid_uuid(self, authorized_client):
        response = authorized_client.get("/users/invalid-uuid")
        assert response.status_code == 422

    def test_get_user_by_id_unauthorized(self, created_user, client):
        response = client.get(f"/users/{created_user.id}")
        assert response.status_code == 403
