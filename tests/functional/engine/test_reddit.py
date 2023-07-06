def test_submission(praw_session):
    assert praw_session is not None
    submission_id = "14rre07"
    submission = praw_session.submission(submission_id)
    assert submission is not None
    assert hasattr(submission, "title")