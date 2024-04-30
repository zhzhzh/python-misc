import logging
import sys

from Utils.logging_config import config_local_logger

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    config_local_logger()
    logger.info(sys.version)
    logger.info("Hello World!")
