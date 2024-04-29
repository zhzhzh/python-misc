import logging

print(__name__)
logger = logging.getLogger(__name__)


class MyClass1:
    print(__name__)

    def __init__(self) -> None:
        logger.debug("debug in MyClass1")
        logger.info("info in MyClass1")
        logger.error("error in MyClass1")


class MyClass2:
    print(__name__)
    # logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        logger.debug("debug in MyClass2")
        logger.info("info in MyClass2")
        logger.error("error in MyClass2")
