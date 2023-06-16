import json

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import (
    check_password_hash, generate_password_hash
)


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=True)
    password = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    modules = db.relationship(
        "Module",
        back_populates="user",
        cascade="all, delete, delete-orphan"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User {}>".format(self.username)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="READY")
    stream = db.Column(db.String(10), nullable=False)
    trigger = db.Column(db.Text, nullable=False)
    actions = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.String(50), nullable=True)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="modules")

    triggered_submissions = db.relationship(
        "TriggeredSubmission",
        back_populates="module",
        cascade="all, delete, delete-orphan"
    )
    triggered_comments = db.relationship(
        "TriggeredComment",
        back_populates="module",
        cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return "<Module {}>".format(self.name)

    @property
    def fullname(self):
        return "{}/{}".format(self.user.username, self.name)

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "trigger": self.trigger.to_dict()
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def triggered(self):
        if self.stream == "submission":
            query = TriggeredSubmission.query.filter_by(module_id=self.id)
            return query.order_by(TriggeredSubmission.created.desc())
        elif self.stream == "comment":
            query = TriggeredComment.query.filter_by(module_id=self.id)
            return query.order_by(TriggeredComment.created.desc())


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.String(10), nullable=False, unique=True)
    title = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    subreddit = db.Column(db.String(50), nullable=False)
    url = db.Column(db.Text, nullable=False)
    nsfw = db.Column(db.Boolean, nullable=False)
    permalink = db.Column(db.Text, nullable=False)
    created_utc = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __repr__(self):
        return "<Submission {}>".format(self.submission_id)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.String(10), nullable=False, unique=True)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    subreddit = db.Column(db.String(50), nullable=False)
    permalink = db.Column(db.Text, nullable=False)
    created_utc = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __repr__(self):
        return "<Comment {}>".format(self.comment_id)


class TriggeredSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(
        db.Integer,
        db.ForeignKey("module.id"),
        nullable=False
    )
    module = db.relationship("Module", back_populates="triggered_submissions")
    submission_id = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    subreddit = db.Column(db.String(50), nullable=False)
    url = db.Column(db.Text, nullable=False)
    nsfw = db.Column(db.Boolean, nullable=False)
    permalink = db.Column(db.Text, nullable=False)
    created_utc = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __repr__(self):
        return "<TriggeredSubmission {}>".format(self.submission_id)

    @property
    def fullname(self):
        return "t3_{}".format(self.submission_id)

    def to_dict(self):
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "title": self.title,
            "body": self.body,
            "author": self.author,
            "subreddit": self.subreddit,
            "url": self.url,
            "nsfw": self.nsfw,
            "permalink": self.permalink,
            "created_utc": self.created_utc,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class TriggeredComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(
        db.Integer,
        db.ForeignKey("module.id"),
        nullable=False
    )
    module = db.relationship("Module", back_populates="triggered_comments")
    comment_id = db.Column(db.String(10), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    subreddit = db.Column(db.String(50), nullable=False)
    permalink = db.Column(db.Text, nullable=False)
    created_utc = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __repr__(self):
        return "<TriggeredComment {}>".format(self.comment_id)

    @property
    def fullname(self):
        return "t1_{}".format(self.comment_id)

    def to_dict(self):
        return {
            "id": self.id,
            "comment_id": self.commend_id,
            "body": self.body,
            "author": self.author,
            "subreddit": self.subreddit,
            "permalink": self.permalink,
            "created_utc": self.created_utc,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
