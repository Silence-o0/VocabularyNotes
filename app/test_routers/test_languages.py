from app.services import languages as lang_service


class TestCreateLang:
    """POST /users/"""

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

    def test_create_language_non_admin_user(self, authorized_client):
        lang_data = {"code": "en-UK", "name": "English"}
        response = authorized_client.post("/languages/", json=lang_data)
        assert response.status_code == 403
