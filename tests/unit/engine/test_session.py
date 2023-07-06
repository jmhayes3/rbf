import praw

from rbf.engine.session import get_session


def test_session_class():
    session = get_session()
    assert isinstance(session, praw.Reddit)