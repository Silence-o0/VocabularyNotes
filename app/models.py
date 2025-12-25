from __future__ import annotations

import uuid
from datetime import datetime
from enum import IntEnum

from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declared_attr,
    mapped_column,
    relationship,
)

from app.utils.auth_utils import pwd_context
from app.utils.datetime_utils import utc_now

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class UserRole(IntEnum):
    Admin = 4
    FullAccessUser = 3
    AuthorizedUser = 2
    UnauthorizedUser = 1


class Base(MappedAsDataclass, DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()


dictlist_words = Table(
    "dictlist_words",
    Base.metadata,
    Column(
        "dictlist_id",
        Integer,
        ForeignKey("dictlist.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "word_id", Integer, ForeignKey("word.id", ondelete="CASCADE"), nullable=False
    ),
    PrimaryKeyConstraint("dictlist_id", "word_id", name="dictlist_word_pk"),
)


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default_factory=uuid.uuid4, init=False
    )
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False, repr=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="role_enum"), default=UserRole.UnauthorizedUser
    )
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now, init=False)

    dict_lists: Mapped[list[DictList]] = relationship(
        "DictList",
        back_populates="user",
        cascade="all, delete-orphan",
        init=False,
        repr=False,
    )
    words: Mapped[list[Word]] = relationship(
        "Word", back_populates="user", init=False, repr=False
    )

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)


class DictList(Base):
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        init=False,
    )
    lang_code: Mapped[str | None] = mapped_column(
        ForeignKey("language.code"), init=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now, init=False)
    user: Mapped[User] = relationship("User", back_populates="dict_lists", repr=False)
    language: Mapped[Language | None] = relationship(
        "Language", back_populates="dict_lists", repr=False
    )
    max_words_limit: Mapped[int | None] = mapped_column(default=200)
    words: Mapped[list[Word]] = relationship(
        "Word",
        secondary=dictlist_words,
        back_populates="dict_lists",
        init=False,
        repr=False,
    )


class Word(Base):
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    lang_code: Mapped[str] = mapped_column(ForeignKey("language.code"), init=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        init=False,
    )
    new_word: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now, init=False)
    user: Mapped[User] = relationship("User", back_populates="words", repr=False)
    language: Mapped[Language] = relationship(
        "Language", back_populates="words", repr=False
    )
    contexts_list: AssociationProxy[list[str]] = association_proxy(
        "contexts",
        "context",
        init=False,
    )
    translation: Mapped[str | None] = mapped_column(default=None)
    note: Mapped[str | None] = mapped_column(default=None)
    dict_lists: Mapped[list[DictList]] = relationship(
        "DictList",
        secondary=dictlist_words,
        back_populates="words",
        init=False,
        repr=False,
    )
    contexts: Mapped[list[WordContext]] = relationship(
        "WordContext",
        back_populates="word",
        init=False,
        repr=False,
        cascade="all, delete-orphan",
    )


class WordContext(Base):
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    word_id: Mapped[int] = mapped_column(
        ForeignKey("word.id", ondelete="CASCADE"), init=False
    )
    context: Mapped[str] = mapped_column(nullable=False)

    word: Mapped[Word] = relationship(
        "Word", back_populates="contexts", init=False, repr=False
    )


class Language(Base):
    code: Mapped[str] = mapped_column(String(5), primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    dict_lists: Mapped[list[DictList]] = relationship(
        "DictList", back_populates="language", init=False, repr=False
    )
    words: Mapped[list[Word]] = relationship(
        "Word", back_populates="language", init=False, repr=False
    )
