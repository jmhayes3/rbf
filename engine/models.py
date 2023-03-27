from sqlalchemy import (
    Column, Integer, String, Text, Date, Float,
    DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base, db_session
from .helpers import profile, timeit


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    email = Column(String(320), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    modules = relationship(
        "Module",
        back_populates="user",
        cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return "<User {}>".format(self.username)


class Module(Base):
    __tablename__ = "module"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    status = Column(String(10), nullable=False, default="READY")
    stream = Column(String(10), nullable=False)
    trigger = Column(Text, nullable=False)
    actions = Column(Text, nullable=True)
    refresh_token = Column(String(50), nullable=True)
    created = Column(DateTime(timezone=False), server_default=func.now())
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="modules")

    triggered_submissions = relationship(
        "TriggeredSubmission",
        back_populates="module",
        cascade="all, delete, delete-orphan"
    )
    triggered_comments = relationship(
        "TriggeredComment",
        back_populates="module",
        cascade="all, delete, delete-orphan"
    )

    @property
    def fullname(self):
        return "{}/{}".format(self.user.username, self.name)

    @staticmethod
    # @timeit
    def insert_triggered_submission(module_id, submission):
        with db_session() as session:
            module = session.query(Module).get(module_id)
            triggered = TriggeredSubmission(
                module=module,
                submission_id=submission.get("submission_id"),
                title=submission.get("title"),
                author=submission.get("author"),
                body=submission.get("body"),
                url=submission.get("url"),
                subreddit=submission.get("subreddit"),
                nsfw=submission.get("nsfw"),
                permalink=submission.get("permalink"),
                created_utc=submission.get("created_utc"),
            )
            session.add(triggered)
            session.commit()

    @staticmethod
    # @timeit
    def insert_triggered_comment(module_id, comment):
        with db_session() as session:
            module = session.query(Module).get(module_id)
            triggered = TriggeredComment(
                module=module,
                comment_id=comment.get("comment_id"),
                body=comment.get("body"),
                author=comment.get("author"),
                subreddit=comment.get("subreddit"),
                permalink=comment.get("permalink"),
                created_utc=comment.get("created_utc"),
            )
            session.add(triggered)
            session.commit()

    @staticmethod
    # @timeit
    def update_status(module_id, status):
        with db_session() as session:
            module = session.query(Module).get(module_id)
            module.status = status
            session.commit()

    @staticmethod
    # @timeit
    def get(module_id):
        with db_session() as session:
            module = session.query(Module).get(module_id)
            return module

    @staticmethod
    # @timeit
    def enabled():
        with db_session() as session:
            modules = session.query(Module) \
                                .filter(Module.status == "RUNNING") \
                                .all()
            return modules

    def __repr__(self):
        return "<Module {}>".format(self.name)


class Submission(Base):
    __tablename__ = "submission"
    id = Column(Integer, primary_key=True)
    submission_id = Column(String(15), nullable=False, unique=True)
    title = Column(String(300), nullable=False)
    url = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    author = Column(String(50), nullable=False)
    subreddit = Column(String(50), nullable=False)
    nsfw = Column(Boolean, nullable=False)
    permalink = Column(String, nullable=False)
    created_utc = Column(Float, nullable=False)
    created = Column(DateTime(timezone=False), server_default=func.now())

    def __repr__(self):
        return "<Submission {}>".format(self.submission_id)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    comment_id = Column(String(15), nullable=False, unique=True)
    body = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    subreddit = Column(String(50), nullable=False)
    permalink = Column(String, nullable=False)
    created_utc = Column(Float, nullable=False)
    created = Column(DateTime(timezone=False), server_default=func.now())

    def __repr__(self):
        return "<Comment {}>".format(self.comment_id)


class TriggeredSubmission(Base):
    __tablename__ = "triggered_submission"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("module.id"), nullable=False)
    module = relationship("Module", back_populates="triggered_submissions")
    submission_id = Column(String(10), nullable=False)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    subreddit = Column(String(50), nullable=False)
    url = Column(String, nullable=False)
    nsfw = Column(Boolean, nullable=False)
    permalink = Column(String, nullable=False)
    created_utc = Column(Float, nullable=False)
    created = Column(DateTime(timezone=False), server_default=func.now())

    def __repr__(self):
        return "<TriggeredSubmission {}>".format(self.submission_id)

    @property
    def fullname(self):
        return "t3_{}".format(self.submission_id)


class TriggeredComment(Base):
    __tablename__ = "triggered_comment"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("module.id"), nullable=False)
    module = relationship("Module", back_populates="triggered_comments")
    comment_id = Column(String(10), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    subreddit = Column(String(50), nullable=False)
    permalink = Column(String, nullable=False)
    created_utc = Column(Float, nullable=False)
    created = Column(DateTime(timezone=False), server_default=func.now())

    def __repr__(self):
        return "<TriggeredComment {}>".format(self.comment_id)

    @property
    def fullname(self):
        return "t1_{}".format(self.comment_id)
