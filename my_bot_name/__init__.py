import datetime
import logging
import os
import sys
from argparse import ArgumentParser
from functools import wraps
from pathlib import Path
from typing import Callable

import yaml

PACKAGE_LOCATION = Path(os.path.dirname(__file__))
ROOT_LOCATION = PACKAGE_LOCATION.parent
RESOURCES_LOCATION = PACKAGE_LOCATION / "resources"
CONFIG_LOCATION = RESOURCES_LOCATION / "config"

LOGGER_NAME = "common"
LOGGING_FORMAT = "%(asctime)s | %(levelname)-8s | %(module)-20s| %(message)s"


def _init_logger():
    """It sets the format of Python root logger"""
    formatter = logging.Formatter(LOGGING_FORMAT)

    # Create stream handler for stdout with INFO level
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    logs_dir = ROOT_LOCATION / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create file handler with timestamp in filename and DEBUG level
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"my_bot_name_{timestamp}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Setup logger with both handlers
    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # Set logger level to DEBUG so file handler can receive debug messages
    logger.setLevel(logging.DEBUG)


_init_logger()
logger = logging.getLogger(LOGGER_NAME)


def log(func: Callable):
    """Decorator to log function calls on start and end"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__

        try:
            logger.info(f"Calling function '{func_name}'")
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            logger.error(f"Error in function '{func_name}': {str(e)}")
            raise e

    return wrapper


def _get_config_dict(env: str) -> dict:
    """Get the config dictionary from resource file"""

    with open(os.path.join(CONFIG_LOCATION, "{}.yml".format(env))) as f:
        configmap = yaml.load(f, Loader=yaml.SafeLoader)
    return configmap if configmap else {}


def _get_env() -> str:
    """Get the environment (first from command line, otherwise from env variable, otherwise local)"""

    parser = ArgumentParser()
    parser.add_argument(
        "-e",
        "--environment",
        default=os.environ.get("ENVIRONMENT", "local"),
        help="environment",
    )
    args, _ = parser.parse_known_args()
    return args.environment


def _deep_merge(dict1, dict2):
    """
    Recursively merge dictionaries.
    Values in dict2 override those in dict1 unless both values are dicts,
    in which case they are recursively merged.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


environment = _get_env()
config = _deep_merge(_get_config_dict("default"), _get_config_dict(environment))
