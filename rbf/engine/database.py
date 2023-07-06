from sqlalchemy import create_engine
from sqlalchemy import select, update, insert
from sqlalchemy.sql import text

from models import (
    Base,
    AppUser,
    Module,
    Submission,
    Comment,
    TriggeredSubmission,
    TriggeredComment,
)


class Database:

    def __init__(self, database_uri, echo=False):
        self.database_uri = database_uri
        self.echo = echo

    def init_db(self):
        self.engine = create_engine(self.database_uri, echo=self.echo)

    def close_db(self):
        self.engine.dispose()

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def drop_all(self):
        Base.metadata.drop_all(self.engine)

    def get_module(self, module_id):
        with self.engine.connect() as conn:
            stmt = select(Module.id, Module.trigger).where(Module.id == module_id)
            result = conn.execute(stmt)
            return result.first()

    def update_module_status(self, module_id, value):
        with self.engine.connect() as conn:
            stmt = update(Module).where(Module.id == module_id).values(status=value)
            conn.execute(stmt)

    def get_active_modules(self):
        with self.engine.connect() as conn:
            query = text(
                """
                SELECT id, name, status FROM module ORDER BY id
                """
            )
            result = conn.execute(query)
            return result.all()

    def insert_submission(self, submission):
        with self.engine.connect() as conn:
            stmt = insert(Submission).values(**submission)
            result = conn.execute(stmt)
            conn.commit()

    def insert_triggered_submission(self, module_id, submission):
        with self.engine.connect() as conn:
            stmt = insert(TriggeredSubmission).values(module_id=module_id, **submission)
            result = conn.execute(stmt)
            conn.commit()

    def insert_comment(self, comment):
        with self.engine.connect() as conn:
            stmt = insert(Comment).values(**comment)
            result = conn.execute(stmt)
            conn.commit()

    def insert_triggered_comment(self, module_id, comment):
        with self.engine.connect() as conn:
            stmt = insert(TriggeredComment).values(module_id=module_id, **comment)
            result = conn.execute(stmt)
            conn.commit()
