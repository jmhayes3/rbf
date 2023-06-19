import os
import time
import logging
import traceback

import zmq

from rbf.engine.database import Database
from rbf.engine.responder import Responder


HEALTHCHECK_INTERVAL = 5.0

logger = logging.getLogger(__name__)


class Worker:

    def __init__(self):
        # TODO: Generate a uuid for id.
        self.id = os.getpid()

        self.responders = []
        self.bots = {}

        self.db = Database()

        self.seen_submissions = 0
        self.seen_comments = 0

        self.ctx = zmq.Context()

        # Sink for bot load requests.
        # TODO: Measure time elapsed from original send to recieve.
        # Test how long it takes before a message gets handled using
        # different numbers of workers.
        self.collector = self.ctx.socket(zmq.PULL)

        # Bind socket to address. Connect using PUSH sockets from clients.
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

    def load_responder(self, responder_id):
        """Load bot from db."""

        module = self.db.get_module(responder_id)
        if module:
            responder = Responder(module[0], module[1])
            self.responders.append(responder)
            self.db.update_module_status(responder_id, "RUNNING")

    def on_submission(self, submission) -> None:
        if submission:
            self.seen_submissions += 1
            for responder in self.responders:
                triggered = responder.process_submission(submission)
                if triggered:
                    self.db.insert_triggered_submission(
                        responder.id,
                        submission
                    )

    def on_comment(self, comment) -> None:
        if comment:
            self.seen_comments += 1
            for responder in self.responders:
                triggered = responder.process_comment(comment)
                if triggered:
                    self.db.insert_triggered_comment(
                        responder.id,
                        comment
                    )

    def on_load(self, payload) -> None:
        print(f"Load request received: {payload}")

        responder = payload.get("responder")
        loaded = self.load_responder(responder)

    def shutdown(self):
        self.subscriber.close()
        self.collector.close()
        self.ctx.term()

    def start(self):
        print(f"Worker {self.id} started")
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

                    if message == "load":
                        self.on_load(payload)

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
