#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)

migrate = Migrate(app, db)
db.init_app(app)


@app.route("/")
# Root health check
def index():
    return {"message": "Chatterbox API running"}, 200


def get_payload():
    """
    Prefer JSON (React / Postman raw JSON), but fallback to form/query params
    to be resilient for tests or alternate clients.
    """
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data

    # fallback
    merged = {}
    merged.update(request.args.to_dict())
    merged.update(request.form.to_dict())
    return merged


@app.route("/messages", methods=["GET"])
# List messages
def messages_index():
    messages = (
        Message.query
        .order_by(Message.created_at.asc())
        .all()
    )
    return make_response([m.to_dict() for m in messages], 200)


@app.route("/messages", methods=["POST"])
# Create message
def messages_create():
    data = get_payload()

    body = data.get("body")
    username = data.get("username")

    missing = []
    if body is None or str(body).strip() == "":
        missing.append("body")
    if username is None or str(username).strip() == "":
        missing.append("username")

    if missing:
        return make_response(
            {"errors": ["Validation errors"], "missing": missing},
            400
        )

    message = Message(body=body, username=username)
    db.session.add(message)
    db.session.commit()

    return make_response(message.to_dict(), 201)


@app.route("/messages/<int:id>", methods=["PATCH"])
# Update message body
def messages_update(id):
    message = Message.query.filter(Message.id == id).first()

    if message is None:
        return make_response({"message": "Message not found"}, 404)

    data = get_payload()
    new_body = data.get("body")

    if new_body is None or str(new_body).strip() == "":
        return make_response(
            {"errors": ["Validation errors"] , "missing": ["body"]},
            400
        )

    message.body = new_body
    db.session.commit()

    return make_response(message.to_dict(), 200)


@app.route("/messages/<int:id>", methods=["DELETE"])
# Delete message
def messages_delete(id):
    message = Message.query.filter(Message.id == id).first()

    if message is None:
        return make_response({"message": "Message not found"}, 404)

    db.session.delete(message)
    db.session.commit()
    db.session.expunge_all()

    return make_response({"delete_successful": True}, 200)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
