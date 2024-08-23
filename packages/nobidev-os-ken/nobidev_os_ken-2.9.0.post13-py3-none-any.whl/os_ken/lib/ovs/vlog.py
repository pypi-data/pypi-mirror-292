import logging

from ovs.vlog import LEVELS, Vlog


def handler(vlog, level, message):
    logging.getLogger(vlog.name).log(LEVELS.get(level.lower()), f'{vlog.name}: {message}')


def set_handler_for_vlog():
    Vlog.set_handler(handler)
