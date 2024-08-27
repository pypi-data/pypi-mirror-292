import logging
import sys


def configure_logging(log_level):
    logging.basicConfig(
        level=log_level,
        format="%(name)s - %(levelname)s > %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # logging.FileHandler("app.log", mode="a")
        ],
    )
