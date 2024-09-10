from flask import Flask

app = Flask(__name__)

about_me = {
    "name": "Igor",
    "email": "XJQp7@example.com",
}


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


if __name__ == "__main__":
    app.run(debug=True)
