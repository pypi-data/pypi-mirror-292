from __future__ import annotations

import logging.config
import os

import coloredlogs
import yaml


def setupLogging(
    default_path="../config/logger.yaml",
    default_level=logging.INFO,
    env_key="LOG_CFG",
):
    """
    This method sets up the logging configuration for the application.
    :param default_path: path to the YAML configuration file (default: '../config/logger.yaml')
    :param default_level: default log level if the configuration file is not found (default: logging.INFO)
    :param env_key: environment variable key to specify the path to the configuration file (default: 'LOG_CFG')
    :return: None
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value

    try:
        if os.path.exists(path):
            with open(path) as f:
                config = yaml.safe_load(f.read())
                if "logging" in config:
                    logging.config.dictConfig(config["logging"])
                    coloredlogs.install()
                else:
                    raise ValueError("'logging' not found in the configuration file")
        else:
            raise FileNotFoundError(f"Configurations file not found at path: {path}")
    except Exception as e:
        print(f"Error in loading logging configurations: {e}")
        print("Using default logging configurations")
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)


if __name__ == "__main__":
    setupLogging()
    logger = logging.getLogger(__name__)
    logger.debug("Debug inside the function")
    logger.info("Info inside the function")
    logger.warning("Warning inside the function")
    logger.error("Error inside the function")
    logger.critical("Critical inside the function")
