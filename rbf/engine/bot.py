"""
The Bot class is comprised of a stream (comment or submission),
a target (subreddit), a trigger, and an action.

Replaces the Responder class.
"""

from triggers import Contains, Regex, Keyword
from actions import Log


class Bot:

    def __init__(self, trigger, action, stream="submission", target="all"):
        self.trigger = trigger
        self.action = action

        # submission or comment
        self.stream = stream

        # subreddit
        self.target = target

    def process_item(self, item):
        if item["stream"] == "submission":
            self.process_submission(item)
        elif item["stream"] == "comment":
            self.process_comment(item)
        else:
            return None

    def process_submission(self, submission):
        assert submission["stream"] == "submission"

    def process_comment(self, comment):
        assert comment["stream"] == "comment"