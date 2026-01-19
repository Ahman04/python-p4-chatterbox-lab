#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
app.json.compact = False


@app.route("/")
def index():
    return {"message": "Chatterbox API running"}, 200


@app.route("/messages", methods=["GET"])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages]), 200


@app.route("/messages", methods=["POST"])
def create_message():
    data = request.get_json()

    message = Message(
        body=data.get("body"),
        username=data.get("username")
    )
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201


@app.route("/messages/<int:id>", methods=["PATCH"])
def update_message(id):
    message = Message.query.get(id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()

    if "body" in data:
        message.body = data["body"]
    db.session.commit()

    return jsonify(message.to_dict()), 200


@app.route("/messages/<int:id>", methods=["DELETE"])
def delete_message(id):
    message = Message.query.get(id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()

    return {}, 204


if __name__ == "__main__":
    app.run(port=5555, debug=True)
