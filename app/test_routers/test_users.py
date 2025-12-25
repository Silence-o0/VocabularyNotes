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

        user = user_service.get_user_by_email(data["email"], db_session)
        expected_data = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
        }
        assert response.json() == expected_data
        assert user.password != data["password"]

    def test_create_user_missing_fields(self, client, mock_send_verification_email):
        incomplete_data = {"username": "testuser"}
        response = client.post("/users/", json=incomplete_data)
        assert response.status_code == 422
        mock_send_verification_email.assert_not_called()


class TestLogin:
    """POST /auth/login"""

    def test_login_success(self, client, user):
        login_data = {
            "username": user.username,
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

    def test_login_wrong_password(self, client, user):
        login_data = {"username": user.username, "password": "wrongpassword"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 400


class TestGetCurrentUser:
    """GET /users/me"""

    def test_get_current_user_success(self, authorized_client, user, db_session):
        response = authorized_client.get("/users/me")
        assert response.status_code == 200

        user_db = user_service.get_user_by_id(user.id, db_session)
        expected_data = {
            "id": str(user_db.id),
            "username": user_db.username,
            "email": user_db.email,
            "role": user_db.role,
            "created_at": user_db.created_at.isoformat(),
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

    def test_update_username_success(self, authorized_client, user, db_session):
        update_data = {"username": "new_username"}
        response = authorized_client.patch(
            "/users/me/change_username", json=update_data
        )
        assert response.status_code == 200

        updated_user = user_service.get_user_by_id(user.id, db_session)
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

    def test_update_email_duplicate(self, authorized_client, another_user):
        update_data = {"email": another_user.email}
        response = authorized_client.patch("/users/me/change_email", json=update_data)
        assert response.status_code == 409


class TestUpdatePassword:
    """PATCH /users/me/change_password"""

    def test_update_password_success(self, authorized_client, user, db_session):
        update_data = {
            "old_password": "securepassword123",
            "new_password": "newsecurepassword456",
        }
        response = authorized_client.patch(
            "/users/me/change_password", json=update_data
        )
        assert response.status_code == 200

        updated_user = user_service.get_user_by_id(user.id, db_session)
        assert updated_user.verify_password(update_data["new_password"])

    def test_update_password_wrong_old_password(self, authorized_client):
        update_data = {
            "old_password": "wrongpassword",
            "new_password": "newsecurepassword456",
        }
        response = authorized_client.patch(
            "/users/me/change_password", json=update_data
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

    def test_delete_user_success(self, authorized_client, user, db_session):
        response = authorized_client.delete("/users/me")
        assert response.status_code == 204
        with pytest.raises(NotFoundError):
            user_service.get_user_by_id(user.id, db_session)

    def test_delete_user_unauthorized(self, client):
        response = client.delete("/users/me")
        assert response.status_code == 403


class TestGetUserById:
    """GET /users/{user_id}"""

    def test_get_user_by_id_success(self, authorized_client_as_admin, another_user):
        response = authorized_client_as_admin.get(f"/users/{another_user.id}")
        assert response.status_code == 200
        assert response.json() == {
            "id": str(another_user.id),
            "username": another_user.username,
            "email": another_user.email,
            "role": another_user.role,
            "created_at": another_user.created_at.isoformat(),
        }

    def test_get_user_by_id_not_found(self, authorized_client_as_admin):
        non_existent_id = uuid.uuid4()
        response = authorized_client_as_admin.get(f"/users/{non_existent_id}")
        assert response.status_code == 404

    def test_get_user_by_id_invalid_uuid(self, authorized_client_as_admin):
        response = authorized_client_as_admin.get("/users/invalid-uuid")
        assert response.status_code == 422

    def test_get_user_by_id_unauthorized(self, user, client):
        response = client.get(f"/users/{user.id}")
        assert response.status_code == 403

    def test_get_user_by_id_non_admin(self, authorized_client, another_user):
        response = authorized_client.get(f"/users/{another_user.id}")
        assert response.status_code == 403


class TestGetAllUsers:
    """GET /users/"""

    def test_admin_can_get_all_users(self, authorized_client_as_admin):
        response = authorized_client_as_admin.get("/users/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_admin_can_get_users_filter_by_role(
        self, authorized_client_as_admin, another_user
    ):
        response = authorized_client_as_admin.get("/users/?role=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["username"] == another_user.username

    def test_non_admin_cannot_get_all_users(self, authorized_client):
        response = authorized_client.get("/users/")
        assert response.status_code == 403
