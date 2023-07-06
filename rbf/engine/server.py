import os
import time
import logging
import multiprocessing as mp

from dotenv import load_dotenv

from publishers import comment_publisher, submission_publisher
from worker import Worker
from database import Database


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Server:

    def __init__(self, workers=2) -> None:
        load_dotenv()

        self.workers = workers
        self.worker_processes = []

        self.submission_publisher = mp.Process(target=submission_publisher)
        self.comment_publisher = mp.Process(target=comment_publisher)

    def start(self) -> None:
        logger.info("Server started")

        self.db = Database(os.environ["DATABASE_URI"])
        self.db.init_db()
        self.db.create_all()
        self.db.close_db()

        time.sleep(1)

        for _ in range(self.workers):
            worker_process = Worker()
            worker_process.start()
            self.worker_processes.append(worker_process)

        self.submission_publisher.start()
        self.comment_publisher.start()


def main():
    server = Server(workers=2)
    server.start()


if __name__ == "__main__":
    main()
