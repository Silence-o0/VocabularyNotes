import pytest
from app.exceptions import NotFoundError
from app.services import languages as lang_service
from app import schemas


class TestCreateLang:
    """POST /languages/"""

    def test_create_lang_success(self, authorized_client_as_admin):
        lang_data = {"code": "en-UK", "name": "English"}
        response = authorized_client_as_admin.post("/languages/", json=lang_data)
        assert response.status_code == 201
        assert response.json() == lang_data

    def test_create_user_missing_fields(self, authorized_client_as_admin):
        incomplete_data = {
            "code": "en-UK",
        }
        response = authorized_client_as_admin.post("/languages/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_language_invalid_code_length(
        self, authorized_client_as_admin, db_session
    ):
        wrong_data = {"code": "english", "name": "English"}
        response = authorized_client_as_admin.post("/languages/", json=wrong_data)
        assert response.status_code == 422
        assert lang_service.get_all_languages(db_session) == []

    def test_create_language_non_admin(self, authorized_client):
        lang_data = {"code": "en-UK", "name": "English"}
        response = authorized_client.post("/languages/", json=lang_data)
        assert response.status_code == 403


class TestDeleteLanguage:
    """DELETE /languages/{lang_code}"""

    def test_delete_language_success(self, authorized_client_as_admin, db_session, language):
        response = authorized_client_as_admin.delete(f"/languages/{language.code}")
        assert response.status_code == 204
        with pytest.raises(NotFoundError):
            lang_service.get_language_by_code(language.code, db_session)

    def test_delete_language_not_found(self, authorized_client_as_admin):
        response = authorized_client_as_admin.delete("/languages/nonexistent")
        assert response.status_code == 404

    def test_delete_language_non_admin(self, authorized_client, db_session, language):
        response = authorized_client.delete(f"/languages/{language.code}")
        assert response.status_code == 403


class TestGetAllUsers:
    """GET /languages/all"""

    def test_get_all_languages(self, client):
        response = client.get("/languages/all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
