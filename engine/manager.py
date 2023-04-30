import logging
import multiprocessing
import os
import sys
import threading
import time
import traceback

import zmq
from dotenv import load_dotenv

from .database import Database
from .publishers import comment_publisher, submission_publisher
from .worker import Worker

load_dotenv()

WORKER_TTL = 5.0


class Manager:

    def __init__(self, num_workers=1, load_modules=True, reload_workers=False):
        """Distribute work to workers and manage their lifecycles."""

        self.logger = logging.getLogger(__name__)

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

        # Should be a separate process.
        self.submission_publisher = threading.Thread(target=submission_publisher)
        self.submission_publisher.daemon = True

        # Should be a separate process.
        self.comment_publisher = threading.Thread(target=comment_publisher)
        self.comment_publisher.daemon = True

        self.poller = zmq.Poller()
        self.poller.register(self.collector, zmq.POLLIN)
        self.poller.register(self.messenger, zmq.POLLIN)

        self.db = Database()

        self.num_workers = num_workers
        self.load_modules = load_modules
        self.reload_workers = reload_workers

        self.worker_processes = []

        self.active_workers = {}

    def spawn_worker(self, **kwargs):
        worker = multiprocessing.Process(
            target=run_worker,
            kwargs=dict(**kwargs),
            daemon=True
        )
        worker.start()
        self.worker_processes.append(worker)

    def spawn_workers(self):
        for _ in range(self.num_workers):
            self.spawn_worker()

    def kill_worker(self, process, tries=3, wait=0.1, sigkill=False):
        while tries and process.is_alive():
            process.terminate()
            tries -= 1
            time.sleep(wait)
        if sigkill:
            time.sleep(wait)
            if process.is_alive():
                process.kill()

    def kill_workers(self):
        for process in self.worker_processes:
            self.kill_worker(process)

    def add_active_worker(self, worker):
        self.active_workers[worker] = dict()
        self.active_workers[worker]["TTL"] = time.time() + WORKER_TTL
        self.active_workers[worker]["responders"] = []
        self.logger.info("Worker {} connected".format(worker))

    def remove_active_worker(self, worker):
        self.active_workers.pop(worker)

    def update_active_worker(self, worker):
        self.active_workers[worker]["TTL"] = time.time() + WORKER_TTL

    def check_active_workers(self):
        for worker in self.active_workers.copy():
            if time.time() > self.active_workers[worker]["TTL"]:
                self.logger.warning("Worker {} timed out".format(worker))
                for process in self.worker_processes:
                    if process.is_alive() and process.pid == worker:
                        self.kill_worker(process)
                if self.reload_workers:
                    self.spawn_worker(reload=True, id=worker)
                self.remove_active_worker(worker)

    def on_heartbeat(self, payload):
        worker = payload.get("worker_id")
        if worker not in self.active_workers.keys():
            self.add_active_worker(worker)
        else:
            self.update_active_worker(worker)

    def on_killed(self, payload):
        worker = payload.get("worker_id")
        responder = payload.get("responder")
        self.active_workers[worker]["responders"].remove(responder)
        self.logger.info("Responder {} killed by worker {}".format(
                responder,
                worker
            )
        )

    def on_loaded(self, payload):
        worker = payload.get("worker_id")
        responder = payload.get("responder")
        self.active_workers[worker]["responders"].append(responder)
        self.logger.info("Responder {} loaded by worker {}".format(
                responder,
                worker
            )
        )

    def on_load(self, payload):
        self.logger.debug("Load request received: {}".format(payload))
        self.distributor.send_json({
            "context": "load",
            "payload": {
                "responder": payload
            }
        })

    def on_kill(self, payload):
        self.logger.debug("Kill request received: {}".format(payload))
        self.broadcaster.send_json({
            "context": "kill",
            "payload": {
                "responder": payload
            }
        })

    def shutdown(self):
        self.kill_workers()
        self.broadcaster.close()
        self.distributor.close()
        self.collector.close()
        self.messenger.close()
        self.ctx.term()
        sys.exit(0)

    def reload(self):
        modules = self.db.get_active_modules()
        for module in modules:
            print(module)
            self.distributor.send_json({
                "context": "load",
                "payload": {
                    "responder": module[0]
                }
            })

    def start(self):
        self.logger.info("Manager started")
        # Spawn worker processes before publishers so that subscribers are
        # already listening.
        self.spawn_workers()

        # Give workers time to initialize.
        time.sleep(1)

        if self.load_modules:
            self.reload()

        # self.queue_processor.start()
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
                self.check_active_workers()
            except KeyboardInterrupt:
                self.shutdown()
            except zmq.ZMQError:
                self.logger.error(
                    traceback.format_exc()
                )
                sys.exit(-1)
            except Exception:
                self.logger.critical("Uncaught exception: {}".format(
                        traceback.format_exc()
                    )
                )
                sys.exit(-1)
