from app import schemas


class TestCreateWord:
    """POST /words/"""

    def test_create_word_success(self, authorized_client, user, language):
        word_data = {
            "new_word": "animal",
            "translation": "тварина",
            "note": "some notes",
            "lang_code": "en-UK",
            "contexts": [
                "Wild animals live in the forest",
                " My favorite animal is a dog ",
                ""
            ]
        }
        response = authorized_client.post("/words/", json=word_data)
        assert response.status_code == 201

        data = response.json()
        expected_data = {
            "id": data["id"],
            "user_id": str(user.id),
            "new_word": word_data["new_word"],
            "translation": word_data["translation"],
            "note": word_data["note"],
            "language": schemas.LanguageSchema.model_validate(language).model_dump(),
            "created_at": data["created_at"],
            "contexts": [
                "Wild animals live in the forest",
                "My favorite animal is a dog"
            ]
        }
        assert data == expected_data

    def test_create_word_minimal_data(self, authorized_client, language):
        word_data = {
            "new_word": "animal",
            "lang_code": "en-UK",
        }
        response = authorized_client.post("/words/", json=word_data)
        assert response.status_code == 201

        data = response.json()
        assert data["new_word"] == word_data["new_word"]
        assert (
            data["language"]
            == schemas.LanguageSchema.model_validate(language).model_dump()
        )

    def test_create_word_nonexist_lang_code(self, authorized_client):
        word_data = {
            "new_word": "animal",
            "lang_code": "en",
        }
        response = authorized_client.post("/words/", json=word_data)
        assert response.status_code == 400

    def test_create_word_unauthorized(self, client, language):
        word_data = {
            "new_word": "animal",
            "lang_code": "en-UK",
        }
        response = client.post("/words/", json=word_data)
        assert response.status_code == 403
