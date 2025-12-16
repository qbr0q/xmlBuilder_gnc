import logging

from settings import log_file_name


def setup_log():
    logging.basicConfig(
        level=logging.DEBUG,
        filename=log_file_name,
        filemode='a',
        encoding='utf-8'
    )
