import os
import sys
import traceback
import logging
import praw
import zmq


def get_session():
    logger = logging.getLogger(__name__)

    # needs a refresh_token or username and password
    try:
        session = praw.Reddit(
            user_agent=os.environ.get("DESCRIPTION"),
            client_id=os.environ.get("APP_KEY"),
            client_secret=os.environ.get("APP_SECRET"),
            password=os.environ.get("PASSWORD"),
            username=os.environ.get("USERNAME"),
            # refresh_token=os.environ.get("REFRESH_TOKEN"),
        )
    except Exception:
        logger.error("Uncaught exception: {}".format(traceback.format_exc()))
        sys.exit(-1)

    return session


def submission_publisher(subreddit="all"):
    """
    Stream submissions from reddit and send them to subscribers (workers).
    """
    logger = logging.getLogger(__name__)
    ctx = zmq.Context()
    publisher = ctx.socket(zmq.PUB)
    publisher.bind(os.getenv("SUBMISSION_PUBLISHER_URI"))

    session = get_session()
    subreddit = session.subreddit(subreddit)
    submissions = subreddit.stream.submissions(pause_after=-1)

    logger.info("Submission stream opened")

    for submission in submissions:
        if submission is not None:
            submission_data = {
                "submission_id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "body": submission.selftext,
                "subreddit": submission.subreddit.display_name,
                "permalink": submission.permalink,
                "nsfw": submission.over_18,
                "created_utc": submission.created_utc,
            }

            try:
                submission_data["author"] = submission.author.name
            except AttributeError:
                submission_data["author"] = "[unknown]"

            publisher.send_json({
                "context": "submission",
                "payload": submission_data
            })


def comment_publisher(subreddit="all"):
    """
    Stream comments from reddit and send them to subscribers (workers).
    """
    logger = logging.getLogger(__name__)
    ctx = zmq.Context()
    publisher = ctx.socket(zmq.PUB)
    publisher.bind(os.getenv("COMMENT_PUBLISHER_URI"))

    session = get_session()
    subreddit = session.subreddit(subreddit)
    comments = subreddit.stream.comments(pause_after=-1)

    logger.info("Comment stream opened")

    for comment in comments:
        if comment is not None:
            comment_data = {
                "comment_id": comment.id,
                "body": comment.body,
                "permalink": comment.permalink,
                "subreddit": comment.subreddit.display_name,
                "created_utc": comment.created_utc,
            }

            try:
                comment_data["author"] = comment.author.name
            except AttributeError:
                comment_data["author"] = "[unknown]"

            publisher.send_json({
                "context": "comment",
                "payload": comment_data
            })
