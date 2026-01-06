from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()


class Message(db.Model, SerializerMixin):
    __tablename__ = "messages"

    serialize_rules = ()  # keep default serialization simple

    id = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Message id={self.id} username={self.username}>"
