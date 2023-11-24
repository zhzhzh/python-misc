import logging
import random
import time
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
            f"Running for {hours} hours, internal {interval} seconds, loop {times} times"
        )

        for i in range(1, times):
            x1 = random.randint(0, self.x)
            y1 = random.randint(0, self.y)
            screen.moveTo(x1, y1)
            self.logger.info(f"{i}: move to ({x1}, {y1})")
            time.sleep(interval)


if __name__ == "__main__":
    logger = get_stream_logger(LOGGER_NAME)

    mouse_mover = MouseMover(logger=logger)
    mouse_mover.random_move()
