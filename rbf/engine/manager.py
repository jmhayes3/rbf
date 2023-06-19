import multiprocessing

from rbf.engine.publishers import (
    comment_publisher,
    submission_publisher
)


class Manager:

    def __init__(self) -> None:
        # Run as a separate process.
        self.submission_publisher = multiprocessing.Process(target=submission_publisher)

        # Run as a separate process.
        self.comment_publisher = multiprocessing.Process(target=comment_publisher)

    def start(self) -> None:
        self.submission_publisher.start()
        self.comment_publisher.start()


if __name__ == "__main__":
    manager = Manager()
    manager.start()
