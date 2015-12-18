import logging
import sys


FMT = "%(asctime)s %(levelname)s %(message)s"


def setup_logging(level=logging.DEBUG, stream=sys.stderr):
    logging.basicConfig(stream=stream, level=getattr(logging, level),
                        format=FMT)
