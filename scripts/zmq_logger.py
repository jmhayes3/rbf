import logging
import time

from zmq.log.handlers import PUBHandler

zmq_log_handler = PUBHandler("tcp://127.0.0.1:12345")
zmq_log_handler.setFormatter(logging.Formatter(fmt='{name} > {message}', style='{'), logging.DEBUG)
zmq_log_handler.setRootTopic("events")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(zmq_log_handler)

time.sleep(1)

while True:
    logger.debug("In loop")
    time.sleep(1)
    logger.info("some event occurred")
