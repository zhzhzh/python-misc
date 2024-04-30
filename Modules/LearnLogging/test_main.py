import logging

from LearnLogging.my_class import MyClass1, MyClass2
from LearnLogging.my_class_new import MyClass3, MyClass4
from Utils.logging_config import config_local_logger

logger = logging.getLogger(__name__)


def print_logger(logger: logging.Logger):
    print("--->")
    print(
        f"\tlogger_name: {logger.name}, level: {logger.level}, propagate: {logger.propagate}, disabled: {logger.disabled}"
    )
    print(f"\thandler_cnt: {len(logger.handlers)}, {logger.handlers}")
    for handler in logger.handlers:
        print(f"\t\thandler_name: {handler.name}, level: {handler.level}, {handler}")
    print("<---")


if __name__ == "__main__":
    config_local_logger()
    logger_name = "test"
    test_logger = logging.getLogger(logger_name)

    test_logger.setLevel(logging.DEBUG)

    logger_format = (
        "[%(asctime)s] %(levelname)s\t[%(module)s.%(funcName)s:%(lineno)s] %(message)s"
    )
    formatter = logging.Formatter(logger_format)

    # add the StreamHandler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    test_logger.addHandler(ch)
    test_logger.info("test_logger: add a StreamHandler.")

    # print("=========")
    # print_logger(logging.getLogger())
    # print_logger(logging.getLogger(logger_name))
    # print_logger(logging.getLogger("LearnLogging"))
    # print_logger(logging.getLogger("LearnLogging.my_class"))
    test_logger.info("after LOGGING: test_logger: add a StreamHandler.")

    logger = logging.getLogger()
    logger.debug("debug in main")
    logger.info("info in main")
    logger.error("error in main")

    class1 = MyClass1()
    class2 = MyClass2()
    class3 = MyClass3()
    class4 = MyClass4()
    print_logger(logging.getLogger())
    print_logger(logging.getLogger("LearnLogging"))
    print_logger(logging.getLogger("LearnLogging.my_class"))
