from app import schemas


class TestCreateDictList:
    """POST /dictlists/"""

    def test_create_dictlist_success(self, authorized_client, user, language):
        dictlist_data = {
            "name": "My Vocabulary",
            "lang_code": "en-UK",
            "max_words_limit": 100,
        }
        response = authorized_client.post("/dictlists/", json=dictlist_data)
        assert response.status_code == 201

        data = response.json()
        expected_data = {
            "id": data["id"],
            "user_id": str(user.id),
            "language": schemas.LanguageSchema.model_validate(language).model_dump(),
            "name": dictlist_data["name"],
            "created_at": data["created_at"],
            "max_words_limit": dictlist_data["max_words_limit"],
        }
        assert data == expected_data

    def test_create_dictlist_minimal_data(self, authorized_client, language):
        dictlist_data = {
            "name": "My Vocabulary",
        }

        response = authorized_client.post("/dictlists/", json=dictlist_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == dictlist_data["name"]

    def test_create_dictlist_nonexist_lang_code(self, authorized_client):
        dictlist_data = {
            "name": "My Vocabulary",
            "lang_code": "en",
            "max_words_limit": 100,
        }
        response = authorized_client.post("/dictlists/", json=dictlist_data)
        assert response.status_code == 400

    def test_create_dictlist_unauthorized(self, client, language):
        dictlist_data = {"name": "My Vocabulary", "lang_code": language.code}
        response = client.post("/dictlists/", json=dictlist_data)
        assert response.status_code == 403
