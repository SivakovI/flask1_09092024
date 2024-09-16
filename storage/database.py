import sqlite3
from enum import Enum
from pathlib import Path

from flask import g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates

MIN_RATING = 1
MAX_RATING = 5
DEFAULT_RATING = 1


def validate_rating(rating):
    return MIN_RATING <= rating <= MAX_RATING


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class QuoteModel(db.Model):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(
        Integer(),
        CheckConstraint(f"rating >= {MIN_RATING} AND rating <= {MAX_RATING}"),
        default=DEFAULT_RATING,
    )

    def __init__(self, author, text, rating) -> None:
        self.author = author
        self.text = text
        self.rating = rating

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text,
            "rating": self.rating,
        }

    @validates("rating")
    def orm_validate_rating(self, _, rating):
        if validate_rating(rating):
            return rating
        raise ValueError(f"Rating must be between {MIN_RATING} and {MAX_RATING}")


class ReturnType(Enum):
    ONE = 1
    ALL = 2
    LASTROWID = 3
    ROWCOUNT = 4


BASE_DIR = Path(__file__).parent.parent
path_to_db = f"sqlite:///{BASE_DIR / "store.db"}"


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(path_to_db)
        db.row_factory = make_dicts
    return db


def query_db(query, args=(), return_tupe: ReturnType = ReturnType.ALL):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    match return_tupe:
        case ReturnType.ONE:
            return rv[0] if rv else None
        case ReturnType.ALL:
            return rv if rv else None
        case ReturnType.LASTROWID:
            return cur.lastrowid
        case ReturnType.ROWCOUNT:
            return cur.rowcount


def get_quote_by_id(id):
    return db.get_or_404(QuoteModel, id, description=f"Quote with id {id} not found")


def populate_db():
    if db.session.query(QuoteModel).count() > 0:
        return

    quotes = [
        QuoteModel(
            "Говард Лавкрафт",
            (
                "Мы живём на тихом островке невежества посреди "
                "темного моря бесконечности, и нам вовсе не следует плавать на далекие "
                "расстояния."
            ),
            5,
        ),
        QuoteModel(
            "Говард Лавкрафт",
            (
                "Человек может играть силами природы лишь до "
                "определенных пределов; то, что вы создали, обернется против вас."
            ),
            5,
        ),
    ]

    for quote in quotes:
        db.session.add(quote)

    db.session.commit()
