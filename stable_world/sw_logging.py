import os
import logging
import time

from .env import env


class Formatter(logging.Formatter):
    def __init__(self, fmt):
        logging.Formatter.__init__(self, fmt)
        self.last = time.time()

    def format(self, record):
        current = time.time()
        record.delta = '%sms' % int((current - self.last) * 1000 // 1)
        self.last = current

        return logging.Formatter.format(self, record)


def setup_logging():

    if not env.DEBUG:
        logging.getLogger().addHandler(logging.NullHandler())
        return

    log_names = env.DEBUG.split(os.pathsep)

    handler = logging.StreamHandler()
    handler.setFormatter(Formatter('[+%(delta)s|%(name)s] %(message)s'))

    for log_name in log_names:
        if log_name == '*':
            log_name = None  # Root

        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
