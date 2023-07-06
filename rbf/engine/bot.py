"""
The Bot class is comprised of a stream (comment or submission),
a target (subreddit), a trigger, and an action.

Replaces the Responder class.
"""

from triggers import Contains, Regex, Keyword
from actions import Log


class Bot:

    def __init__(self, trigger, action, stream="submission", subreddit=None):
        self.trigger = trigger
        self.action = action

        # submission or comment
        self.stream = stream

        # subreddit
        self.subreddit = subreddit

    def process_submission(self, submission):
        if self.subreddit == "all":
            return submission["submission_id"]
        elif self.subreddit == submission["subreddit"]:
            return submission["submission_id"]

        return None

    def process_comment(self, comment):
        if self.subreddit == "all":
            return comment["comment_id"]
        elif self.subreddit == comment["subreddit"]:
            return comment["comment_id"]

        return None