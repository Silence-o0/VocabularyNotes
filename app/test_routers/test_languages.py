import pytest

from app.exceptions import NotFoundError
from app.services import languages as lang_service


class TestCreateLang:
    """POST /languages/"""

    def test_create_lang_success(self, authorized_client_as_admin):
        lang_data = {"code": "en-UK", "name": "English"}
        response = authorized_client_as_admin.post("/languages/", json=lang_data)
        assert response.status_code == 201
        assert response.json() == lang_data

    def test_create_lang_missing_fields(self, authorized_client_as_admin):
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

    def test_delete_language_success(
        self, authorized_client_as_admin, db_session, language
    ):
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


class TestGetAllLanguages:
    """GET /languages/all"""

    def test_get_all_languages(self, client):
        response = client.get("/languages/all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGetLanguageByCode:
    """GET /languages/{lang_code}"""

    def test_get_language_by_code_success(self, client, language):
        response = client.get(f"/languages/{language.code}")
        assert response.status_code == 200
        assert response.json() == {
            "code": language.code,
            "name": language.name,
        }

    def test_get_languages_by_code_not_found(self, client):
        response = client.get("/languages/code")
        assert response.status_code == 404


class TestUpdateLangName:
    """PATCH /languages/{lang_code}"""

    def test_update_name_success(
        self, authorized_client_as_admin, language, db_session
    ):
        new_name = "British English"
        response = authorized_client_as_admin.patch(
            f"/languages/{language.code}", params={"new_name": new_name}
        )
        assert response.status_code == 200
        updated_language = lang_service.get_language_by_code(language.code, db_session)
        assert updated_language.name == new_name

    def test_update_lang_name_non_admin(self, client, language):
        new_name = "British English"
        response = client.patch(
            f"/languages/{language.code}", params={"new_name": new_name}
        )
        assert response.status_code == 403

    def test_update_lang_name_not_found(self, authorized_client_as_admin):
        response = authorized_client_as_admin.patch(
            "/languages/nonexistent", params={"new_name": "New Name"}
        )
        assert response.status_code == 404

    def test_update_lang_name_empty_name(self, authorized_client_as_admin, language):
        response = authorized_client_as_admin.patch(
            f"/languages/{language.code}", params={"new_name": ""}
        )
        assert response.status_code == 422
