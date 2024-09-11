from http import HTTPStatus
from random import choice

from flask import Flask, request

app = Flask(__name__)

about_me = {
    "name": "Igor",
    "email": "XJQp7@example.com",
}

quotes = [
    {
        "id": 3,
        "author": "Rick Cook",
        "text": (
            "Программирование сегодня — это гонка разработчиков программ, "
            "стремящихся писать программы с большей и лучшей "
            "идиотоустойчивостью, и вселенной, которая пытается создать "
            "больше отборных идиотов. Пока вселенная побеждает."
        ),
    },
    {
        "id": 5,
        "author": "Waldi Ravens",
        "text": (
            "Программирование на С похоже на быстрые танцы на только что "
            "отполированном полу людей с острыми бритвами в руках."
        ),
    },
    {
        "id": 6,
        "author": "Mosher’s Law of Software Engineering",
        "text": (
            "Не волнуйтесь, если что-то не работает. Если бы всё "
            "работало, вас бы уволили."
        ),
    },
    {
        "id": 8,
        "author": "Yoggi Berra",
        "text": ("В теории, теория и практика неразделимы. На практике это не так."),
    },
]


def get_quote_by_id(id):
    for index, quote in enumerate(quotes):
        if quote["id"] == id:
            return quote, index

    return None, None


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


@app.route("/quotes")
def get_quotes():
    return quotes


@app.route("/quotes", methods=["POST"])
def add_quote():
    quote = request.json
    quote["id"] = quotes[-1]["id"] + 1
    quotes.append(quote)
    return quote, HTTPStatus.CREATED


@app.route("/quotes/<int:id>")
def get_quote(id):
    quote, _ = get_quote_by_id(id)
    if quote is None:
        return f"Quote with id {id} not found", HTTPStatus.NOT_FOUND

    return quote, HTTPStatus.OK


@app.route("/quotes/<int:id>", methods=["PUT"])
def edit_quote(id):
    quote, index = get_quote_by_id(id)
    if quote is None:
        return f"Quote with id {id} not found", HTTPStatus.NOT_FOUND

    new_data = request.json

    for key, value in new_data.items():
        if key not in quote:
            return f"Invalid key {key}", HTTPStatus.BAD_REQUEST
        if key == "id":
            return "Id is read-only", HTTPStatus.BAD_REQUEST

        quote[key] = value

    quotes[index] = quote

    return quote, HTTPStatus.OK


@app.route("/quotes/<int:id>", methods=["DELETE"])
def delete_quote(id):
    quote, index = get_quote_by_id(id)
    if quote is None:
        return f"Quote with id {id} not found", HTTPStatus.NOT_FOUND

    del quotes[index]
    return f"Quote with id {id} deleted", HTTPStatus.OK


@app.route("/quotes/count")
def get_quote_count():
    return {"count": len(quotes)}


@app.route("/quotes/random")
def get_random_quote():
    return choice(quotes)


if __name__ == "__main__":
    app.run(debug=True)
