import logging
from functools import wraps
from inspect import ismethod
from pprint import pformat


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;2m"
    blue = "\x1b[34;1m"
    yellow = "\x1b[33;1m"
    red = "\x1b[31;1m"
    blink_red = "\x1b[31;5m"
    r = "\x1b[0m"

    prefix = (
        "[%(levelname)s]"
    )

    message = (
        " %(message)s |%(filename)s:%(lineno)d "
    )

    postfix = (
        "|%(asctime)s"
    )

    FORMATS = {
        logging.DEBUG: blue + prefix + r + grey + message + r + postfix + r,
        logging.INFO: grey + prefix + r + grey + message + r + postfix + r,
        logging.WARNING: yellow + prefix + r + message + yellow + postfix + r,
        logging.ERROR: red + prefix + r + message + red + postfix + r,
        logging.CRITICAL: blink_red + prefix + r + message + red + postfix + r}

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


LOG = logging.getLogger('maqet')

ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
LOG.propagate = True
LOG.addHandler(ch)


def debug(func):
    if ismethod(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            signature = f"{args[0].__name__}.{
                func.__name__}({args[1:]}, {kwargs})"
            LOG.debug(f"{signature}")
            r = func(*args, **kwargs)
            LOG.debug(f"{signature} \n-> {r}")
            return r
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            signature = f"{func.__name__}({args}, {kwargs})"
            LOG.debug(f"{signature}")
            r = func(*args, **kwargs)
            LOG.debug(f"{signature} \n-> {r}")
            return r
    return wrapper


PFORMAT = pformat
