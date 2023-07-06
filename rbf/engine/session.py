import os

import praw


def get_session():
    session = praw.Reddit(
        user_agent=os.environ.get("APP_USER_AGENT"),
        client_id=os.environ.get("APP_KEY"),
        client_secret=os.environ.get("APP_SECRET"),
        password=os.environ.get("APP_PASSWORD"),
        username=os.environ.get("APP_USERNAME"),
    )
    return session