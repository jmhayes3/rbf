import time
import logging
import traceback
import uuid

import zmq

from rbf.engine.database import Database
from rbf.engine.bot import Bot


HEALTHCHECK_INTERVAL = 5.0

logger = logging.getLogger(__name__)


class Worker:

    def __init__(self):
        self._uuid = uuid.uuid4()
        print(f"UUID: {self._uuid}")

        self.bots = {}

        self.db = Database()

        self.seen_submissions = 0
        self.seen_comments = 0

        self.ctx = zmq.Context()

        # Sink for bot load requests.
        # TODO: Measure time elapsed from original send to recieve.
        # Test how long it takes before a message gets handled using
        # different numbers of workers.
        self.collector = self.ctx.socket(zmq.SUB)

        # Bind socket to address. Connect using PUB sockets from clients.
        self.collector.bind("tcp://127.0.0.1:5557")

        self.subscriber = self.ctx.socket(zmq.SUB)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # Subscribe to submission publisher.
        self.subscriber.connect("tcp://127.0.0.1:5560")

        # Subscribe to comment publisher.
        self.subscriber.connect("tcp://127.0.0.1:5561")

        self.poller = zmq.Poller()
        self.poller.register(self.collector, zmq.POLLIN)
        self.poller.register(self.subscriber, zmq.POLLIN)

    def load_bot(self, bot_id):
        module = self.db.get_module(bot_id)
        if module:
            bot = Bot(None, None)
            self.bots[bot] = "RUNNING"
            self.db.update_module_status(bot_id, "RUNNING")

    def kill_bot(self, bot_id):
        bot = self.bots.pop(bot_id)

        print(f"Bot {bot} killed.")

    def on_submission(self, submission) -> None:
        if submission:
            self.seen_submissions += 1
            for bot in self.bots:
                triggered = bot.process_submission(submission)
                if triggered:
                    self.db.insert_triggered_submission(
                        bot.id,
                        submission
                    )

    def on_comment(self, comment) -> None:
        if comment:
            self.seen_comments += 1
            for bot in self.bots:
                triggered = bot.process_comment(comment)
                if triggered:
                    self.db.insert_triggered_comment(
                        bot.id,
                        comment
                    )

    def on_load(self, bot) -> None:
        print(f"Load request received for bot: {bot}")

        loaded = self.load_bot(bot)

    def on_kill(self, bot) -> None:
        print(f"Kill request received for bot: {bot}")

        killed = self.kill_bot(bot)

    def shutdown(self):
        self.subscriber.close()
        self.collector.close()
        self.ctx.term()

    def start(self):
        print(f"Worker {self._uuid} started")
        print(f"Database: {self.db.engine}")

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
                    elif context == "kill":
                        self.on_kill(bot=payload)

                if self.subscriber in events:
                    message = self.subscriber.recv_json()
                    context = message["context"]
                    payload = message["payload"]

                    if context == "submission":
                        self.on_submission(submission=payload)
                    elif context == "comment":
                        self.on_comment(comment=payload)

                if time.time() >= alarm:
                    alarm = time.time() + HEALTHCHECK_INTERVAL
                    print(f"Bots: {self.bots}")
                    print(f"Seen submissions: {self.seen_submissions}")
                    print(f"Seen comments: {self.seen_comments}")
            except KeyboardInterrupt:
                self.shutdown()
            except zmq.ZMQError:
                logger.error(msg=traceback.format_exc())


if __name__ == "__main__":
    worker = Worker()
    worker.start()
