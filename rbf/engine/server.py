import multiprocessing

from dotenv import load_dotenv

from rbf.engine.publishers import comment_publisher, submission_publisher
from rbf.engine.worker import Worker


class Server:

    def __init__(self) -> None:
        load_dotenv()

        # Run as a separate process.
        self.submission_publisher = multiprocessing.Process(target=submission_publisher)

        # Run as a separate process.
        self.comment_publisher = multiprocessing.Process(target=comment_publisher)

        self.worker = Worker()

    def start(self) -> None:
        self.submission_publisher.start()
        self.comment_publisher.start()

        # Blocking.
        self.worker.start()


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
