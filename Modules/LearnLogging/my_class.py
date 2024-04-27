import logging


class MyClass:
    print(__name__)
    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self.logger.debug("debug in MyClass")
        self.logger.info("info in MyClass")
        self.logger.error("error in MyClass")
