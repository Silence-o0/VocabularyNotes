import uuid
from datetime import datetime
from enum import IntEnum

from sqlalchemy import (
    TIMESTAMP,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declared_attr,
    mapped_column,
    relationship,
)

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


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4, init=False
    )
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="role_enum", values_callable=lambda x: [e.name for e in x]),
        default=UserRole.UnauthorizedUser,
        init=False,
    )
    created: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), init=False
    )
    full_access_deadline: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("(now() + interval '356 days')"), init=False
    )

    dict_lists: Mapped[list["DictList"]] = relationship(
        "DictList", back_populates="user", cascade="all, delete-orphan", init=False
    )


class DictList(Base):
    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(default="General", nullable=False)
    max_words_limit: Mapped[int | None] = mapped_column(default=200)
    created: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), init=False
    )

    __table_args__ = (PrimaryKeyConstraint("id", "user_id", name="dictlist_pk"),)

    user: Mapped["User"] = relationship("User", back_populates="dict_lists", init=False)
