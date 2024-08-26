import logging
import logging.config
import logging.handlers
import os
import sys


def get_logging_level(level_name: str) -> int:
    level_name = level_name.upper()
    level_map = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }
    _v = level_map.get(level_name, None)
    if _v is None: raise ValueError(f"Invalid log level: {level_name}")
    return _v


class SimpleLogLoader:

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        except Exception:
            raise

        path = os.path.join(base_path, relative_path)
        logging.info(f"log setup file path: {path}")
        return path

    @staticmethod
    def setup_simple(log_level: int = logging.DEBUG,
                     log_file_absolute_path: str = None,
                     log_file_name: str = None):
        default_log_format = "[%(levelname)7s][%(process)10d][%(asctime)s][%(name)s][%(filename)s][%(funcName)s] - %(message)s"
        default_log_date_format = "%Y-%m-%d %H:%M:%S"

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(logging.Formatter(fmt=default_log_format, datefmt=default_log_date_format))

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(stream_handler)

        if log_file_absolute_path is not None and log_file_name is not None:
            file_path = log_file_absolute_path + os.path.sep + log_file_name
            file_handler = logging.handlers.TimedRotatingFileHandler(file_path, when='midnight', backupCount=30, interval=1, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(fmt=default_log_format, datefmt=default_log_date_format))
            root_logger.addHandler(file_handler)
            logging.info(f"default log setup. stream handler, file handler. log file path: {file_path}")
        else:
            logging.info(f"default log setup. stream handler.")

    @staticmethod
    def setup_config(config_path: str = None):
        if config_path is None:
            raise ValueError("config path is None. please check config path.")
        path = SimpleLogLoader.resource_path(config_path)
        logging.config.fileConfig(path, disable_existing_loggers=False, encoding='utf-8')
