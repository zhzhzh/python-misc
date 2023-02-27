import logging
import logging.handlers


def get_time_rotation_file_logger(
    logger_name: str, log_file: str, backup_cnt: int = 7, debug: bool = False
) -> logging.Logger:
    new_logger = logging.getLogger(logger_name)
    logger_level = logging.INFO
    if debug:
        logger_level = logging.DEBUG
    new_logger.setLevel(logger_level)

    logger_format = '[%(asctime)s] %(levelname)s\t[%(module)s.%(funcName)s:%(lineno)s] %(message)s'
    formatter = logging.Formatter(logger_format)

    ch = logging.StreamHandler()
    ch.setLevel(logger_level)
    ch.setFormatter(formatter)
    new_logger.addHandler(ch)

    fh = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', backupCount=backup_cnt
    )
    fh.setFormatter(formatter)
    fh.setLevel(logger_level)
    new_logger.addHandler(fh)
    return new_logger


def get_stream_logger(logger_name: str, logger_level: int = logging.DEBUG) -> logging.Logger:
    new_logger = logging.getLogger(logger_name)
    new_logger.setLevel(logger_level)

    logger_format = '[%(asctime)s] %(levelname)s\t[%(module)s.%(funcName)s:%(lineno)s] %(message)s'
    formatter = logging.Formatter(logger_format)

    ch = logging.StreamHandler()
    ch.setLevel(logger_level)
    ch.setFormatter(formatter)
    new_logger.addHandler(ch)
    return new_logger
