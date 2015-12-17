import logging
import sys


FMT = "%(asctime)s %(level)s %(message)s"


def setup_logging(level=logging.DEBUG, stream=sys.stderr):
    logging.basicConfig(stream=stream, level=level, format=FMT)
