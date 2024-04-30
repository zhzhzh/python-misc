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
        self.x, self.y = screen.size()

    def random_move(self, hours: float = 3.0, interval: int = 25) -> None:
        times = int((hours * 3600) / interval) + 1
        logger.info(
            f"Running for {hours} hours, interval {interval} seconds, loop {times} times"
        )

        step = 10

        for i in range(1, times):
            x_step = random.randint(-step, step)
            y_step = random.randint(-step, step)
            screen.move(x_step, y_step)
            logger.info(
                f"{i} of {times}: step({x_step}, {y_step}), move to {screen.position()}"
            )
            time.sleep(interval)


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
