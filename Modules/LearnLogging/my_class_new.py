import logging

print(__name__)
logger = logging.getLogger(__name__)


class MyClass3:
    print(__name__)

    def __init__(self) -> None:
        logger.debug("debug in MyClass3")
        logger.info("info in MyClass3")
        logger.error("error in MyClass3")


class MyClass4:
    print(__name__)
    # logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        logger.debug("debug in MyClass4")
        logger.info("info in MyClass4")
        logger.error("error in MyClass4")
