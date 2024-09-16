from http import HTTPStatus

from flask import Flask, request
from sqlalchemy.exc import InvalidRequestError

from storage.database import (
    DEFAULT_RATING,
    QuoteModel,
    db,
    get_quote_by_id,
    path_to_db,
    populate_db,
    validate_rating,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = path_to_db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/quotes")
def get_quotes():
    quotes = db.session.query(QuoteModel).all()
    return [quote.to_dict() for quote in quotes]


@app.route("/quotes", methods=["POST"])
def add_quote():
    data = request.json

    if "rating" not in data or not validate_rating(data["rating"]):
        data["rating"] = DEFAULT_RATING

    try:
        quote = QuoteModel(**data)
        db.session.add(quote)
        db.session.commit()
    except TypeError:
        return (
            (
                "Invalid data. Required: author, text, rating (optional). "
                f"Received: {", ".join(data.keys())}"
            ),
            HTTPStatus.BAD_REQUEST,
        )

    return quote.to_dict(), HTTPStatus.CREATED


@app.route("/quotes/filter")
def filter_quotes():
    try:
        quotes = db.session.query(QuoteModel).filter_by(**request.args).all()
    except InvalidRequestError:
        return (
            (
                "Invalid data. Possible keys: author, text, rating. "
                f"Received: {", ".join(request.args.keys())}"
            ),
            HTTPStatus.BAD_REQUEST,
        )

    return [quote.to_dict() for quote in quotes]


@app.route("/quotes/<int:id>")
def get_quote(id):
    return get_quote_by_id(id).to_dict()


@app.route("/quotes/<int:id>", methods=["PUT"])
def edit_quote(id):
    quote = get_quote_by_id(id)

    data = request.json
    if "rating" in data and not validate_rating(data["rating"]):
        data.pop("rating")
    if len(data) == 0:
        return "No valid data to update", HTTPStatus.BAD_REQUEST

    try:
        for key, value in data.items():
            assert hasattr(
                quote, key
            ), f"Invalid key: {key}. Valid: author, text, rating"
            setattr(quote, key, value)
        db.session.commit()
        return quote.to_dict()
    except Exception as e:
        return str(e), HTTPStatus.BAD_REQUEST


@app.route("/quotes/<int:id>", methods=["DELETE"])
def delete_quote(id):
    quote = get_quote_by_id(id)
    db.session.delete(quote)
    return f"Quote with id {id} deleted"


if __name__ == "__main__":
    db.init_app(app)

    with app.app_context():
        db.create_all()
        populate_db()

    app.run(debug=True)
