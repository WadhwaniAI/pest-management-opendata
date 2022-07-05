import os
import logging

__all__ = [
    'Logger',
]

lvl = os.environ.get('PYTHONLOGLEVEL', 'WARNING').upper()
fmt = '[ %(asctime)s %(levelname)s %(filename)s ] %(message)s'
logging.basicConfig(format=fmt,
                    datefmt="%H:%M:%S",
                    level=lvl)
logging.captureWarnings(True)
Logger = logging.getLogger(__name__)
