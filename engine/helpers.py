import csv
import json
import sys
import os
import logging
import binascii
import io
import time
import contextlib
import cProfile
import pstats
import zmq

from functools import wraps
from contextlib import ContextDecorator
from logging.handlers import TimedRotatingFileHandler

LOG_FORMAT = logging.Formatter(
    (
        "%(asctime)s [%(levelname)s]"
        " -- [%(name)s:%(module)s/%(funcName)s]"
        " -- %(message)s"
    ),
    datefmt="%H:%M:%S"
)
LOG_LEVEL = logging.INFO


def setup_logging(log_level=LOG_LEVEL):
    null_handler = logging.NullHandler()
    logging.basicConfig(
        level=log_level,
        handlers=[null_handler]
    )

    # Set handler for logging to console.
    # console_handler = logging.StreamHandler()  # Log to stderr.
    console_handler = logging.StreamHandler(sys.__stdout__)  # Log to stdout.
    console_handler.setLevel(log_level)
    console_handler.setFormatter(LOG_FORMAT)

    logger = logging.getLogger()
    logger.addHandler(console_handler)

    logging.getLogger("praw").setLevel(logging.INFO)
    logging.getLogger("prawcore").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)


def zpipe(ctx):
    """
    Returns a pair of connected 'inproc' PAIR sockets.
    """
    a = ctx.socket(zmq.PAIR)
    b = ctx.socket(zmq.PAIR)
    a.linger = b.linger = 0
    a.hwm = b.hwm = 1
    iface = "inproc://{}".format(binascii.hexlify(os.urandom(8)))
    a.bind(iface)
    b.connect(iface)
    return a, b


def write_to_csv(filename, fieldnames, data):
    with open(filename, mode='w') as csv_file:
        fieldnames = fieldnames
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def write_to_json(filename, data):
    with open(filename, mode='w') as json_file:
        json_data = json.dumps(data)
        json_file.write(json_data)


@contextlib.contextmanager
def profile():
    profile = cProfile.Profile()
    profile.enable()
    yield
    profile.disable()
    stream = io.StringIO()
    stats = pstats.Stats(profile, stream=stream).sort_stats("cumulative")
    stats.print_stats()
    # stats.print_callers()
    print(stream.getvalue())


def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        start = time.time()
        result = f(*args, **kw)
        end = time.time()
        elapsed = end - start
        print(f"func: {f.__name__}, args: [{args}, {kw}], time: {elapsed}s")
        return result
    return wrap
