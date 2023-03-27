import time
import logging
import json
import zmq
import boto3


class SQSProcessor(threading.Thread):

    def __init__(self, ctx, pipe, queue_url, interval=1):
        threading.Thread.__init__(self)

        self.logger = logging.getLogger(__name__)
        self.ctx = ctx
        self.pipe = pipe

        sqs = boto3.resource("sqs")
        self.queue = sqs.Queue(queue_url)

        self.interval = interval

    def process_message(self, message):
        message = json.loads(message.body)
        context = message.get("context")
        payload = message.get("payload")
        if context == "kill":
            self.pipe.send_json({
                "context": "kill",
                "payload": {
                    "responder": payload
                }
            })
            return True
        elif context == "load":
            self.pipe.send_json({
                "context": "load",
                "payload": {
                    "responder": payload
                }
            })
            return True
        return False

    def run(self):
        self.logger.info("SQS processor started")
        while True:
            for message in self.queue.receive_messages():
                processed = self.process_message(message)
                if processed:
                    message.delete()
            time.sleep(self.interval)
