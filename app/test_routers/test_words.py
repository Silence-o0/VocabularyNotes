from app import schemas
from app.services import words as word_service


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


class TestGetWordById:
    """GET /words/{word_id}"""

    def test_get_user_word_by_id_success(self, authorized_client, word):
        response = authorized_client.get(f"/words/{word.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["new_word"] == "animal"
        assert data["user_id"] == str(word.user_id)

    def test_get_word_by_id_not_found(self, authorized_client):
        response = authorized_client.get("/words/123")
        assert response.status_code == 404

    def test_get_word_by_id_forbidden(
        self, authorized_client, another_user, language, db_session
    ):
        word = word_service.create_word(
        schemas.WordCreate(new_word="animal", lang_code="en-UK"),
        another_user,
        db_session,
        )
        response = authorized_client.get(f"/words/{word.id}")
        assert response.status_code == 403


class TestGetAllWords:
    """GET /words/"""

    def test_get_all_user_words(self, authorized_client, another_user, language, db_session):
        word_service.create_word(
        schemas.WordCreate(new_word="animal", lang_code="en-UK"),
        another_user,
        db_session,
        )
        response = authorized_client.get("/words/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_user_words_unauthorized(self, client):
        response = client.get("/words/")
        assert response.status_code == 403
