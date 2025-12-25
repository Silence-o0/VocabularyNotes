import pytest

from app import schemas
from app.exceptions import NotFoundError
from app.services import dictlists as dictlist_service
from app.services import words as word_service


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

    def test_create_dictlist_minimal_data(self, authorized_client):
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


class TestGetAllDictLists:
    """GET /dictlists/"""

    def test_get_all_user_dictlists(self, authorized_client, another_user_dictlist):
        response = authorized_client.get("/dictlists/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_user_dictlists_unauthorized(self, client):
        response = client.get("/dictlists/")
        assert response.status_code == 403


class TestGetDictListById:
    """GET /dictlists/{dictlist_id}"""

    def test_get_user_dictlist_by_id_success(self, authorized_client, dictlist):
        response = authorized_client.get(f"/dictlists/{dictlist.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Vocabulary"
        assert data["user_id"] == str(dictlist.user_id)

    def test_get_dictlist_by_id_not_found(self, authorized_client):
        response = authorized_client.get("/dictlists/123")
        assert response.status_code == 404

    def test_get_dictlist_by_id_forbidden(
        self, authorized_client, another_user_dictlist
    ):
        response = authorized_client.get(f"/dictlists/{another_user_dictlist.id}")
        assert response.status_code == 403


class TestDeleteDictList:
    """DELETE /dictlists/{dictlist_id}"""

    def test_delete_dictlist_success(self, authorized_client, dictlist, db_session):
        response = authorized_client.delete(f"/dictlists/{dictlist.id}")
        assert response.status_code == 204

        with pytest.raises(NotFoundError):
            dictlist_service.get_dictlist_by_id(dictlist.id, db_session)

    def test_delete_dictlist_not_found(self, authorized_client):
        response = authorized_client.delete("/dictlists/12345")
        assert response.status_code == 404

    def test_delete_dictlist_forbidden(
        self, authorized_client, another_user_dictlist, db_session
    ):
        response = authorized_client.delete(f"/dictlists/{another_user_dictlist.id}")
        assert response.status_code == 403


class TestUpdateDictList:
    """PATCH /dictlists/{dictlist_id}"""

    def test_update_dictlist_name_success(
        self, authorized_client, dictlist, db_session
    ):
        response = authorized_client.patch(
            f"/dictlists/{dictlist.id}", json={"name": "New Name"}
        )
        assert response.status_code == 200
        updated_dictlist = dictlist_service.get_dictlist_by_id(dictlist.id, db_session)
        assert updated_dictlist.name == "New Name"
        assert updated_dictlist.language.code == "en-UK"

    def test_update_dictlist_name_none(self, authorized_client, dictlist):
        response = authorized_client.patch(
            f"/dictlists/{dictlist.id}", json={"name": None}
        )
        assert response.status_code == 400

    def test_update_dictlist_language_none_success(
        self, authorized_client, dictlist, db_session
    ):
        response = authorized_client.patch(
            f"/dictlists/{dictlist.id}", json={"lang_code": None}
        )
        assert response.status_code == 200

        updated_dictlist = dictlist_service.get_dictlist_by_id(dictlist.id, db_session)
        assert updated_dictlist.language is None
        assert updated_dictlist.name == "My Vocabulary"

    def test_update_dictlist_not_found(self, authorized_client):
        response = authorized_client.patch(
            "/dictlists/999999", json={"name": "New Name"}
        )
        assert response.status_code == 404

    def test_update_dictlist_other_user(self, authorized_client, another_user_dictlist):
        response = authorized_client.patch(
            f"/dictlists/{another_user_dictlist.id}", json={"name": "Name"}
        )
        assert response.status_code == 403


class TestAssignDictListToWords:
    """POST /dictlists/{dictlist_id}/assign-words"""

    def test_assign_word_to_dictlist(
        self, authorized_client, dictlist, word, db_session
    ):
        response = authorized_client.post(
            f"/dictlists/{dictlist.id}/assign-words", json={"word_ids": [word.id]}
        )
        assert response.status_code == 204
        db_dictlist = dictlist_service.get_dictlist_by_id(dictlist.id, db_session)
        db_word = word_service.get_word_by_id(word.id, db_session)
        assert len(db_dictlist.words) == 1
        assert len(db_word.dict_lists) == 1
        assert db_dictlist.words[0].id == word.id
        assert db_word.dict_lists[0].id == dictlist.id

    def test_assign_empty_wordlist(self, authorized_client, dictlist, db_session):
        response = authorized_client.post(
            f"/dictlists/{dictlist.id}/assign-words", json={"word_ids": []}
        )
        assert response.status_code == 400
        db_dictlist = dictlist_service.get_dictlist_by_id(dictlist.id, db_session)
        assert len(db_dictlist.words) == 0


class TestUnassignDictListFromWords:
    """POST /dictlists/{dictlist_id}/unassign-words"""

    def test_unassign_word_from_dictlist(
        self, authorized_client, dictlist, word, db_session
    ):
        dictlist.words.append(word)
        db_session.commit()

        response = authorized_client.post(
            f"/dictlists/{dictlist.id}/unassign-words",
            json={"word_ids": [word.id]},
        )
        assert response.status_code == 204
        db_dictlist = dictlist_service.get_dictlist_by_id(dictlist.id, db_session)
        assert len(db_dictlist.words) == 0

    def test_unassign_empty_wordlist(
        self,
        authorized_client,
        dictlist,
        db_session,
    ):
        response = authorized_client.post(
            f"/dictlists/{dictlist.id}/unassign-words",
            json={"word_ids": []},
        )
        assert response.status_code == 400
        db_dictlist = dictlist_service.get_dictlist_by_id(dictlist.id, db_session)
        assert len(db_dictlist.words) == 0
