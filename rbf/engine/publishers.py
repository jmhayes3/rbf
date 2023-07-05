import os

import praw
import zmq

from dotenv import load_dotenv


def get_session():
    load_dotenv()
    # needs a refresh_token or username and password
    session = praw.Reddit(
        user_agent=os.environ.get("APP_USER_AGENT"),
        client_id=os.environ.get("APP_KEY"),
        client_secret=os.environ.get("APP_SECRET"),
        password=os.environ.get("APP_PASSWORD"),
        username=os.environ.get("APP_USERNAME"),
        # refresh_token=os.environ.get("APP_REFRESH_TOKEN"),
    )
    return session


def submission_publisher(subreddit="all"):
    """
    Stream submissions from reddit and send them to subscribers (workers).
    """
    ctx = zmq.Context()
    publisher = ctx.socket(zmq.PUB)
    publisher.bind("tcp://127.0.0.1:5560")

    session = get_session()
    subreddit = session.subreddit(subreddit)
    submissions = subreddit.stream.submissions(pause_after=-1)

    print("Submission stream opened")

    for submission in submissions:
        # print(submission)
        if submission is not None:
            submission_data = {
                "submission_id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "body": submission.selftext,
                "subreddit": submission.subreddit.display_name.lower(),
                "permalink": submission.permalink,
                "nsfw": submission.over_18,
                "created_utc": submission.created_utc,
            }

            try:
                submission_data["author"] = submission.author.name
            except AttributeError:
                submission_data["author"] = "[unknown]"

            # print(submission_data)

            publisher.send_json({
                "context": "submission",
                "payload": submission_data
            })


def comment_publisher(subreddit="all"):
    """
    Stream comments from reddit and send them to subscribers (workers).
    """
    ctx = zmq.Context()
    publisher = ctx.socket(zmq.PUB)
    publisher.bind("tcp://127.0.0.1:5561")

    session = get_session()
    subreddit = session.subreddit(subreddit)
    comments = subreddit.stream.comments(pause_after=-1)

    print("Comment stream opened")

    for comment in comments:
        # print(comment)
        if comment is not None:
            comment_data = {
                "comment_id": comment.id,
                "body": comment.body,
                "permalink": comment.permalink,
                "subreddit": comment.subreddit.display_name.lower(),
                "created_utc": comment.created_utc,
            }

            try:
                comment_data["author"] = comment.author.name
            except AttributeError:
                comment_data["author"] = "[unknown]"

            # print(comment_data)

            publisher.send_json({
                "context": "comment",
                "payload": comment_data
            })
