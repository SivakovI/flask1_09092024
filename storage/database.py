from enum import Enum
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)

MIN_RATING = 1
MAX_RATING = 5
DEFAULT_RATING = 1


def validate_rating(rating):
    return MIN_RATING <= rating <= MAX_RATING


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class AuthorModel(db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    quotes: Mapped[list["QuoteModel"]] = relationship(
        back_populates="author", lazy="dynamic"
    )

    def __init__(self, name) -> None:
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class QuoteModel(db.Model):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["AuthorModel"] = relationship(back_populates="quotes")
    text: Mapped[str] = mapped_column(String(255))

    def __init__(self, author, text) -> None:
        self.author = author
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict(),
            "text": self.text,
        }


class ReturnType(Enum):
    ONE = 1
    ALL = 2
    LASTROWID = 3
    ROWCOUNT = 4


BASE_DIR = Path(__file__).parent.parent
path_to_db = f"sqlite:///{BASE_DIR / "store.db"}"


def get_quote_by_id(id):
    return db.get_or_404(QuoteModel, id, description=f"Quote with id {id} not found")


def get_author_by_id(id):
    return db.get_or_404(AuthorModel, id, description=f"Author with id {id} not found")


def populate_db():
    # if db.session.query(QuoteModel).count() > 0:
    #     return

    author = AuthorModel(name="Говард Лавкрафт")
    db.session.add(author)
    db.session.commit()

    quotes = [
        QuoteModel(
            author,
            (
                "Мы живём на тихом островке невежества посреди "
                "темного моря бесконечности, и нам вовсе не следует плавать на далекие "
                "расстояния."
            ),
        ),
        QuoteModel(
            author,
            (
                "Человек может играть силами природы лишь до "
                "определенных пределов; то, что вы создали, обернется против вас."
            ),
        ),
    ]

    for quote in quotes:
        db.session.add(quote)
    db.session.commit()
