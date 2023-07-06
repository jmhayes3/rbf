import os
import time
import logging
import traceback
import uuid
import multiprocessing as mp

import zmq

from database import Database
from bot import Bot


HEALTHCHECK_INTERVAL = 5.0

logger = logging.getLogger(__name__)


class Worker(mp.Process):

    def __init__(self, database_uri=None):
        super(Worker, self).__init__()

        self._uuid = uuid.uuid4()
        self._database_uri = database_uri or os.environ["DATABASE_URI"]

        self.bots = {}

        self.seen_submissions = 0
        self.seen_comments = 0

    def load_bot(self, bot_id):
        module = self.db.get_module(bot_id)

        if module:
            bot = Bot(None, None)
            self.bots[bot_id] = bot
            self.db.update_module_status(module.id, "RUNNING")
            print(f"Bot {bot_id} loaded")

    def kill_bot(self, bot_id):
        bot = self.bots.pop(bot_id)

        if bot:
            self.db.update_module_status(module_id=bot_id, value="STOPPED")
            print(f"Bot {bot_id} killed.")

    def on_submission(self, submission) -> None:
        if submission:
            self.seen_submissions += 1
            self.db.insert_submission(submission=submission)
            for bot_id, bot in self.bots.items():
                triggered = bot.process_submission(submission)
                if triggered:
                    print(f"Bot {bot_id} triggered on submission {triggered}")
                    self.db.insert_triggered_submission(
                        bot_id,
                        submission
                    )

    def on_comment(self, comment) -> None:
        if comment:
            self.seen_comments += 1
            self.db.insert_comment(comment=comment)
            for bot_id, bot in self.bots.items():
                triggered = bot.process_comment(comment)
                if triggered:
                    self.db.insert_triggered_comment(
                        bot_id,
                        comment
                    )

    def on_load(self, bot) -> None:
        print(f"Load request received for bot: {bot}")

        self.load_bot(bot)

    def on_kill(self, bot) -> None:
        print(f"Kill request received for bot: {bot}")

        self.kill_bot(bot)

    def shutdown(self):
        self.subscriber.close()
        self.collector.close()
        self.ctx.term()

    def run(self):
        logger.info("Worker %s started", self._uuid)

        self.db = Database(self._database_uri)

        # Create db engine.
        self.db.init_db()

        # Create db tables if they don't already exist.
        self.db.create_all()

        # Create zmq context for sockets to be bound to.
        self.ctx = zmq.Context()

        # TODO: Measure time elapsed from original send to recieve.
        # Test how long it takes before a message gets handled using
        # different numbers of workers.

        # Sink for bot load requests.
        self.collector = self.ctx.socket(zmq.PULL)
        self.collector.connect(os.environ.get("WEB_URI", "tcp://127.0.0.1:5557"))

        self.subscriber = self.ctx.socket(zmq.SUB)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # Subscribe to submission publisher.
        self.subscriber.connect("tcp://127.0.0.1:5560")

        # Subscribe to comment publisher.
        self.subscriber.connect("tcp://127.0.0.1:5561")

        # TODO: Add additional subscriber for bot kill requests.

        self.poller = zmq.Poller()
        self.poller.register(self.collector, zmq.POLLIN)
        self.poller.register(self.subscriber, zmq.POLLIN)

        alarm = time.time() + HEALTHCHECK_INTERVAL
        while True:
            try:
                events = dict(self.poller.poll(timeout=1000))

                # Check for bots wanting to be loaded first.
                if self.collector in events:
                    message = self.collector.recv_json()
                    context = message["context"]
                    payload = message["payload"]

                    if context == "load":
                        self.on_load(payload)
                elif self.subscriber in events:
                    message = self.subscriber.recv_json()
                    context = message["context"]
                    payload = message["payload"]

                    if context == "submission":
                        self.on_submission(submission=payload)
                    elif context == "comment":
                        self.on_comment(comment=payload)
                    elif context == "kill":
                        self.on_kill(bot=payload)

                if time.time() >= alarm:
                    alarm = time.time() + HEALTHCHECK_INTERVAL
                    logger.info("Bots: %s", self.bots)
                    logger.info("Worker %s seen submissions: %s", self._uuid, self.seen_submissions)
                    logger.info("Worker %s seen comments: %s", self._uuid, self.seen_comments)
            except zmq.ZMQError:
                logger.error(msg=traceback.format_exc())


def main():
    worker = Worker()
    worker.start()


if __name__ == "__main__":
    main()
