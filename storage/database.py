import sqlite3
from enum import Enum
from pathlib import Path

from flask import g


class ReturnType(Enum):
    ONE = 1
    ALL = 2
    LASTROWID = 3
    ROWCOUNT = 4


BASE_DIR = Path(__file__).parent.parent
path_to_db = BASE_DIR / "store.db"


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
    select_quote = "SELECT * from quotes WHERE id = ?"
    quote = query_db(select_quote, (id,), return_tupe=ReturnType.ONE)

    return quote if quote else None
