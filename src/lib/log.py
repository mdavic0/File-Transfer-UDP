import logging
import sys

RED = "\033[91m"
GREEN = "\033[92m"
WHITE = "\033[0m"

error_format = logging.Formatter(
    f"[%(asctime)s] - {RED}[%(levelname)s]: {WHITE}%(message)s")
info_format = logging.Formatter(
    f"[%(asctime)s] - {GREEN}[%(levelname)s]: {WHITE}%(message)s")


class Formatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            return info_format.format(record)
        else:
            return error_format.format(record)


stdout_handler = logging.StreamHandler(sys.stderr)
stdout_handler.setFormatter(Formatter())


def prepare_logger(args):
    logging.basicConfig(level=args, handlers=[stdout_handler])
