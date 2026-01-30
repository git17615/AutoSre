import logging

def setup_logger(name):
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
