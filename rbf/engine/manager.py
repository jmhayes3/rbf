import logging
import multiprocessing
import sys
import time
import traceback

import zmq

from rbf.engine.publishers import comment_publisher, submission_publisher


WORKER_TTL = 5.0

logger = logging.getLogger(name=__name__)


class Manager:

    def __init__(self, verbose=True):
        """Distribute work to workers and manage their lifecycles."""

        self.verbose = verbose

        self.active_workers = {}

        self.ctx = zmq.Context()

        # Broadcast responder kill requests to all workers.
        # Necessary since responder worker destination is not tracked.
        self.broadcaster = self.ctx.socket(zmq.PUB)
        self.broadcaster.bind("tcp://127.0.0.1:5556")

        # Distribute responders to workers in a round-robin fashion.
        self.distributor = self.ctx.socket(zmq.PUSH)
        self.distributor.bind("tcp://127.0.0.1:5557")

        # Sink for receiving messages from workers.
        self.collector = self.ctx.socket(zmq.SUB)
        self.collector.bind("tcp://127.0.0.1:5558")

        # Receive load requests published by frontends.
        self.messenger = self.ctx.socket(zmq.PULL)
        # self.messenger.setsockopt_string(zmq.SUBSCRIBE, "")
        self.messenger.bind("tcp://127.0.0.1:5559")

        self.poller = zmq.Poller()
        self.poller.register(self.collector, zmq.POLLIN)
        self.poller.register(self.messenger, zmq.POLLIN)

        # Should be a separate process.
        self.submission_publisher = multiprocessing.Process(target=submission_publisher)
        self.submission_publisher.daemon = True

        # Should be a separate process.
        self.comment_publisher = multiprocessing.Process(target=comment_publisher)
        self.comment_publisher.daemon = True

    def on_heartbeat(self, payload) -> None:
        worker_id = payload.get("worker_id")
        self.active_workers[worker_id] = dict()
        self.active_workers[worker_id]["TTL"] = time.time() + WORKER_TTL
        self.active_workers[worker_id]["responders"] = []

    def on_killed(self, payload) -> None:
        worker = payload.get("worker_id")
        responder = payload.get("responder")

        self.active_workers[worker]["responders"].remove(responder)

        if self.verbose:
            print(f"Responder {responder} killed by worker {worker}")

    def on_loaded(self, payload) -> None:
        worker = payload.get("worker_id")
        responder = payload.get("responder")

        self.active_workers[worker]["responders"].append(responder)

        if self.verbose:
            print(f"Responder {responder} loaded by worker {worker}")

    def on_load(self, payload) -> None:
        self.distributor.send_json({
            "context": "load",
            "payload": {
                "responder": payload
            }
        })

    def on_kill(self, payload) -> None:
        self.broadcaster.send_json({
            "context": "kill",
            "payload": {
                "responder": payload
            }
        })

    def shutdown(self):
        self.broadcaster.close()
        self.distributor.close()
        self.collector.close()
        self.messenger.close()
        self.ctx.term()
        sys.exit(0)

    def start(self):
        self.submission_publisher.start()
        self.comment_publisher.start()

        while True:
            try:
                events = dict(self.poller.poll(1000))
                if self.collector in events:
                    message = self.collector.recv_json()
                    context = message.get("context")
                    payload = message.get("payload")
                    if context == "heartbeat":
                        self.on_heartbeat(payload)
                    elif context == "loaded":
                        self.on_loaded(payload)
                    elif context == "killed":
                        self.on_killed(payload)
                if self.messenger in events:
                    message = self.messenger.recv_json()
                    context = message.get("context")
                    payload = message.get("payload")
                    if context == "kill":
                        self.on_kill(payload)
                    elif context == "load":
                        self.on_load(payload)
            except KeyboardInterrupt:
                self.shutdown()
            except zmq.ZMQError:
                logger.error(
                    traceback.format_exc()
                )


if __name__ == "__main__":
    manager = Manager()
    manager.start()
