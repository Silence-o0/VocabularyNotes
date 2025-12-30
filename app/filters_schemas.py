from fastapi_filter.contrib.sqlalchemy import Filter

from app import models
from app.schemas import LanguageCode


class UserFilter(Filter):
    role: models.UserRole | None = None

    class Constants(Filter.Constants):
        model = models.User


class DictListFilter(Filter):
    lang_code: LanguageCode | None = None
    word_id: int | None = None

    class Constants(Filter.Constants):
        model = models.DictList


class WordFilter(Filter):
    lang_code: LanguageCode | None = None
    dictlist_id: int | None = None

    class Constants(Filter.Constants):
        model = models.Word
