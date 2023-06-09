import os

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import select, update, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text

Base = declarative_base()


class Database:

    def __init__(self):
        uri = os.getenv("DATABASE_URI")

        self.engine = create_engine(uri, echo=False)

        self.engine.dispose()

    def get_module(self, module_id):
        from .models import Module

        with self.engine.connect() as conn:
            stmt = select(Module.id, Module.trigger).where(Module.id == module_id)
            result = conn.execute(stmt)
            return result.first()

    def update_module_status(self, module_id, value):
        from .models import Module

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

    def insert_triggered_submission(self, module_id, submission):
        from .models import TriggeredSubmission

        with self.engine.connect() as conn:
            stmt = insert(TriggeredSubmission).values(module_id=module_id, **submission)
            result = conn.execute(stmt)
            conn.commit()

    def insert_triggered_comment(self, module_id, comment):
        from .models import TriggeredComment

        with self.engine.connect() as conn:
            stmt = insert(TriggeredComment).values(module_id=module_id, **comment)
            result = conn.execute(stmt)
            conn.commit()
