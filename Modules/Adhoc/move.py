import logging
import logging.config
import random
import time
from argparse import ArgumentParser

import pyautogui as screen

logger = logging.getLogger(__name__)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(funcName)s:%(lineno)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "root": {"handlers": ["console"], "level": "INFO"},
        "__main__": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


class MouseMover:
    def __init__(self) -> None:
        self.x_width, self.y_height = screen.size()
        logger.info(f"x_width: {self.x_width}, y_height: {self.y_height}")

    def random_move(self, hours: float = 3.0, interval: int = 25) -> None:
        times = int((hours * 3600) / interval) + 1
        logger.info(
            f"Running for {hours} hours, interval {interval} seconds, loop {times} times"
        )

        step = 10

        for i in range(1, times):
            # get current position
            current_pos = screen.position()
            x_now = current_pos.x
            y_now = current_pos.y

            # rand steps and get the new position
            x_step = self.random_step(x=int(x_now), step=step, size=self.x_width)
            y_step = self.random_step(x=int(y_now), step=step, size=self.y_height)
            x_new = x_now + x_step
            y_new = y_now + y_step
            logger.info(
                f"before move ({x_now}, {y_now}), steps ({x_step}, {y_step}), to position ({x_new}, {y_new})"
            )
            screen.moveTo(x_new, y_new)
            logger.info(
                f"{i} of {times}: after move step({x_step}, {y_step}), move from {current_pos} to {screen.position()}"
            )
            time.sleep(interval)

    def random_step(self, x: int, step: int, size: int) -> int:
        x_step = random.randint(-step, step)
        x_new = x + x_step
        if x_new <= 0 or x_new >= size:
            logger.info(
                f"Might out of range ({x_new}/ size {size}) after move {x_step}, use other direction"
            )
            x_step = -x_step
        return x_step


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Mouse Mover")
    parser.add_argument("--hours", help="set hours")
    parser.add_argument("--interval", help="set interval in seconds")
    return parser


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)

    args = get_parser().parse_args()
    logger.info(args)

    mouse_mover = MouseMover()

    hours = 3
    if args.hours:
        hours = float(args.hours)

    interval = 25
    if args.interval:
        interval = int(args.interval)

    mouse_mover.random_move(hours=hours, interval=interval)

    logger.info("Done!")
