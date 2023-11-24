import logging
import random
import time
from argparse import ArgumentParser
from logging import Logger

import pyautogui as screen

LOGGER_NAME = "mouse_mover"


def get_stream_logger(logger_name: str, logger_level: int = logging.DEBUG) -> Logger:
    new_logger = logging.getLogger(logger_name)
    new_logger.setLevel(logger_level)

    logger_format = (
        "[%(asctime)s] %(levelname)s\t[%(module)s.%(funcName)s:%(lineno)s] %(message)s"
    )
    formatter = logging.Formatter(logger_format)

    ch = logging.StreamHandler()
    ch.setLevel(logger_level)
    ch.setFormatter(formatter)
    new_logger.addHandler(ch)
    new_logger.info(f"new logger: {logger_name}")
    return new_logger


class MouseMover:
    def __init__(self, logger: Logger) -> None:
        if logger is None:
            self.logger = get_stream_logger(LOGGER_NAME)
        else:
            self.logger = logger
        self.x, self.y = screen.size()

    def random_move(self, hours: int = 3, interval: int = 25) -> None:
        times = int((hours * 3600) / interval) + 1
        self.logger.info(
            f"Running for {hours} hours, interval {interval} seconds, loop {times} times"
        )

        step = 10

        for i in range(1, times):
            x_step = random.randint(-step, step)
            y_step = random.randint(-step, step)
            screen.move(x_step, y_step)
            self.logger.info(
                f"{i}: step({x_step}, {y_step}), move to {screen.position()}"
            )
            time.sleep(interval)


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Mouse Mover")
    parser.add_argument("--hours", help="set hours")
    parser.add_argument("--interval", help="set interval in seconds")
    return parser


if __name__ == "__main__":
    logger = get_stream_logger(LOGGER_NAME)
    args = get_parser().parse_args()
    logger.info(args)

    mouse_mover = MouseMover(logger=logger)

    hours = 3
    if args.hours:
        hours = int(args.hours)

    interval = 25
    if args.interval:
        interval = int(args.interval)

    mouse_mover.random_move(hours=hours, interval=interval)

    logger.info("Done!")
