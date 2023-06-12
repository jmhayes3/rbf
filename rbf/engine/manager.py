import logging
import multiprocessing
import os
import sys
import threading
import time
import traceback

from typing import NoReturn

import zmq

from rbf.engine.publishers import comment_publisher, submission_publisher

WORKER_TTL = 5.0

logger: logging.Logger = logging.getLogger(name=__name__)

class Manager:

    def __init__(self, worker, num_workers=1) -> None:
        """Distribute work to workers and manage their lifecycles."""

        self.pool = []
        self.worker = worker
        self.num_workers = num_workers
        self.active_workers = {}

        self.ctx = zmq.Context()

        # Broadcast responder kill requests to all workers.
        # Necessary since responder worker destination is not tracked.
        self.broadcaster = self.ctx.socket(zmq.PUB)
        self.broadcaster.bind(os.getenv("BROADCASTER_URI"))

        # Distribute responders to workers in a round-robin fashion.
        self.distributor = self.ctx.socket(zmq.PUSH)
        self.distributor.bind(os.getenv("DISTRIBUTOR_URI"))

        # Sink for receiving messages from workers.
        self.collector = self.ctx.socket(zmq.PULL)
        self.collector.bind(os.getenv("COLLECTOR_URI"))

        # Receive load/kill requests published by frontends.
        self.messenger = self.ctx.socket(zmq.PULL)
        # self.messenger.setsockopt_string(zmq.SUBSCRIBE, "")
        self.messenger.bind(os.getenv("MESSENGER_URI"))

        self.poller = zmq.Poller()
        self.poller.register(self.collector, zmq.POLLIN)
        self.poller.register(self.messenger, zmq.POLLIN)

        # Should be a separate process.
        self.submission_publisher = threading.Thread(target=submission_publisher)
        self.submission_publisher.daemon = True

        # Should be a separate process.
        self.comment_publisher = threading.Thread(target=comment_publisher)
        self.comment_publisher.daemon = True

        self.submission_publisher.start()
        self.comment_publisher.start()

    def start(self) -> None:
        for i in range(self.num_workers or 1):
            process = multiprocessing.Process(
                name=f"worker-{i}",
                target=self.worker,
            )
            self.pool.append(process)
            process.start()

        for process in self.pool:
            process.join()

    def terminate(self, *args, **kwargs) -> None:
        while self.pool:
            self.pool.pop().terminate()

    def reload(self, *args, **kwargs) -> None:
        self.terminate()
        self.start()

    def on_heartbeat(self, payload) -> None:
        worker_id = payload.get("worker_id")
        self.active_workers[worker_id] = dict()
        self.active_workers[worker_id]["TTL"] = time.time() + WORKER_TTL
        self.active_workers[worker_id]["responders"] = []

    def on_killed(self, payload) -> None:
        worker = payload.get("worker_id")
        responder = payload.get("responder")

        self.active_workers[worker]["responders"].remove(responder)

        logger.info("Responder {} killed by worker {}".format(responder, worker))

    def on_loaded(self, payload) -> None:
        worker = payload.get("worker_id")
        responder = payload.get("responder")

        self.active_workers[worker]["responders"].append(responder)

        logger.info("Responder {} loaded by worker {}".format(responder, worker))

    def on_load(self, payload) -> None:
        logger.debug("Load request received: {}".format(payload))

        self.distributor.send_json({
            "context": "load",
            "payload": {
                "responder": payload
            }
        })

    def on_kill(self, payload) -> None:
        logger.debug("Kill request received: {}".format(payload))

        self.broadcaster.send_json({
            "context": "kill",
            "payload": {
                "responder": payload
            }
        })

    def shutdown(self) -> NoReturn:
        self.terminate()
        self.broadcaster.close()
        self.distributor.close()
        self.collector.close()
        self.messenger.close()
        self.ctx.term()
        sys.exit(0)

    def eventloop(self) -> NoReturn:
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


class Engine:

    def __init__(self, manager) -> None:
        self.manager = manager
        self.manager.start()

    def eventloop(self) -> NoReturn:
        print("Starting event loop")
        while True:
            print("Beep")
            time.sleep(5)
