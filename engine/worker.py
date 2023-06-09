import os
import sys
import time
import logging
import traceback
import zmq

from database import Database
from responder import Responder

HEARTBEAT_INTERVAL = 1.0

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.id = os.getpid()

        self.ctx = zmq.Context()

        self.subscriber = self.ctx.socket(zmq.SUB)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.subscriber.connect(os.getenv("BROADCASTER_URI"))
        self.subscriber.connect(os.getenv("SUBMISSION_PUBLISHER_URI"))
        self.subscriber.connect(os.getenv("COMMENT_PUBLISHER_URI"))

        self.collector = self.ctx.socket(zmq.PULL)
        self.collector.connect(os.getenv("DISTRIBUTOR_URI"))

        self.publisher = self.ctx.socket(zmq.PUSH)
        self.publisher.connect(os.getenv("COLLECTOR_URI"))

        self.poller = zmq.Poller()
        self.poller.register(self.collector, zmq.POLLIN)
        self.poller.register(self.subscriber, zmq.POLLIN)

        self.responders = []

        self.db = Database()

        self.seen_submissions = 0
        self.seen_comments = 0

    def send_heartbeat(self):
        self.publisher.send_json({
            "context": "heartbeat",
            "payload": {
                "worker_id": self.id,
            }
        })

    def send_status(self):
        self.publisher.send_json({
            "context": "status",
            "payload": {
                "seen_submissions": self.seen_submissions,
                "seen_comments": self.seen_comments,
                "worker_id": self.id,
            }
        })

    def get_responder(self, responder_id):
        for active_responder in self.responders:
            if active_responder.id == responder_id:
                return active_responder

    def load_responder(self, responder_id):
        responder = self.get_responder(responder_id)
        if responder:
            logger.info(
                "Responder {} already loaded".format(responder_id)
            )
            return False
        else:
            module = self.db.get_module(responder_id)
            if module:
                responder = Responder(module[0], module[1])
                self.responders.append(responder)
                logger.info(
                    "Responder {} loaded".format(responder.id)
                )
                self.db.update_module_status(responder_id, "RUNNING")
                return True
            else:
                logger.warning(
                    "Module {} not found".format(responder_id)
                )
                return False

    def kill_responder(self, responder_id):
        responder = self.get_responder(responder_id)
        if responder:
            self.responders.remove(responder)
            logger.info(
                "Responder {} killed".format(responder_id)
            )
            self.db.update_module_status(responder_id, "READY")
            return True
        else:
            logger.info(
                "Responder {} not found".format(responder_id)
            )
            return False

    def on_submission(self, submission):
        if submission:
            self.seen_submissions += 1
            for responder in self.responders:
                triggered = responder.process_submission(submission)
                if triggered:
                    self.db.insert_triggered_submission(
                        responder.id,
                        submission
                    )

    def on_comment(self, comment):
        if comment:
            self.seen_comments += 1
            for responder in self.responders:
                triggered = responder.process_comment(comment)
                if triggered:
                    self.db.insert_triggered_comment(
                        responder.id,
                        comment
                    )

    def on_kill_message(self, payload):
        logger.debug("Kill request received: {}".format(payload))
        responder = payload.get("responder")
        killed = self.kill_responder(responder)
        if killed:
            payload = {
                "responder": responder,
                "worker_id": self.id
            }
            self.publisher.send_json({
                "context": "killed",
                "payload": payload
            })

    def on_load_message(self, payload):
        logger.debug("Load request received: {}".format(payload))
        responder = payload.get("responder")
        loaded = self.load_responder(responder)
        if loaded:
            payload = {
                "responder": responder,
                "worker_id": self.id,
            }
            self.publisher.send_json({
                "context": "loaded",
                "payload": payload
            })

    def shutdown(self):
        self.subscriber.close()
        self.collector.close()
        self.publisher.close()
        self.ctx.term()
        sys.exit(0)

    def start(self):
        logger.info("Worker {} started".format(self.id))
        self.send_heartbeat()
        alarm = time.time() + HEARTBEAT_INTERVAL
        while True:
            try:
                events = dict(self.poller.poll(1000))
                if self.collector in events:
                    message = self.collector.recv_json()
                    context = message.get("context")
                    payload = message.get("payload")
                    if context == "load":
                        self.on_load_message(payload)
                if self.subscriber in events:
                    message = self.subscriber.recv_json()
                    context = message.get("context")
                    payload = message.get("payload")
                    if context == "kill":
                        self.on_kill_message(payload)
                    elif context == "submission":
                        self.on_submission(payload)
                    elif context == "comment":
                        self.on_comment(payload)
                if time.time() >= alarm:
                    self.send_heartbeat()
                    alarm = time.time() + HEARTBEAT_INTERVAL
            except KeyboardInterrupt:
                self.shutdown()
            except zmq.ZMQError:
                logger.error(traceback.format_exc())
