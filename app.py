from http import HTTPStatus

from flask import Flask, g, request

from storage.database import ReturnType, get_quote_by_id, query_db

app = Flask(__name__)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.commit()
        db.close()


@app.route("/quotes")
def get_quotes():
    select_quotes = "SELECT * from quotes"
    quotes = query_db(select_quotes, return_tupe=ReturnType.ALL)

    return quotes


@app.route("/quotes", methods=["POST"])
def add_quote():
    quote = request.json
    add_new_quote = "INSERT INTO quotes (author, text) VALUES (?, ?)"

    quote["id"] = query_db(
        add_new_quote,
        [quote["author"], quote["text"]],
        return_tupe=ReturnType.LASTROWID,
    )

    return quote, HTTPStatus.CREATED


@app.route("/quotes/filter")
def filter_quotes():
    query_parameters = " ,".join(f"{key} = ?" for key in request.args.keys())
    query = f"SELECT * from quotes WHERE {query_parameters}"
    filtered_quotes = query_db(
        query,
        [request.args[key] for key in request.args.keys()],
        return_tupe=ReturnType.ALL,
    )
    return filtered_quotes


@app.route("/quotes/<int:id>")
def get_quote(id):
    quote = get_quote_by_id(id)

    if quote is None:
        return f"Quote with id {id} not found", HTTPStatus.NOT_FOUND

    return quote


@app.route("/quotes/<int:id>", methods=["PUT"])
def edit_quote(id):
    query_parameters = " ,".join(f"{key} = ?" for key in request.json.keys())
    edit_quote_query = f"UPDATE quotes SET {query_parameters} WHERE id = ?"

    try:
        success = query_db(
            edit_quote_query,
            [request.json[key] for key in request.json.keys()] + [id],
            return_tupe=ReturnType.ROWCOUNT,
        )
        if not success:
            return f"Quote with id {id} not found", HTTPStatus.NOT_FOUND

        return get_quote_by_id(id)

    except Exception as e:
        return str(e), HTTPStatus.BAD_REQUEST


@app.route("/quotes/<int:id>", methods=["DELETE"])
def delete_quote(id):
    delete_quote_query = "DELETE FROM quotes WHERE id = ?"

    success = query_db(delete_quote_query, (id,), return_tupe=ReturnType.ROWCOUNT)

    if not success:
        return f"Quote with id {id} not found", HTTPStatus.NOT_FOUND

    return f"Quote with id {id} deleted"


if __name__ == "__main__":
    app.run(debug=True)
