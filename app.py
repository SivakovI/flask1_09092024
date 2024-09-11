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
    for quote in quotes:
        if quote["id"] == id:
            return quote
    return f"Quote with id {id} not found", HTTPStatus.NOT_FOUND


@app.route("/quotes/count")
def get_quote_count():
    return {"count": len(quotes)}


@app.route("/quotes/random")
def get_random_quote():
    return choice(quotes)


if __name__ == "__main__":
    app.run(debug=True)
