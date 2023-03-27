import logging
import json

from .trigger import create_trigger


class Responder:

    def __init__(self, id, trigger, actions=None):
        self.logger = logging.getLogger(__name__)
        self.id = id
        self.trigger = create_trigger(json.loads(trigger))
        self.actions = actions

    def process_submission(self, submission):
        if self.trigger.stream == "submission":
            subreddit = submission.get("subreddit")
            if self.trigger.targets == "all":
                return self.trigger.check_components(submission)
            elif isinstance(self.trigger.targets, list):
                if subreddit.lower() in self.trigger.targets:
                    return self.trigger.check_components(submission)

    def process_comment(self, comment):
        if self.trigger.stream == "comment":
            subreddit = comment.get("subreddit")
            if self.trigger.targets == "all":
                return self.trigger.check_components(comment)
            elif isinstance(self.trigger.targets, list):
                if subreddit.lower() in self.trigger.targets:
                    return self.trigger.check_components(comment)
