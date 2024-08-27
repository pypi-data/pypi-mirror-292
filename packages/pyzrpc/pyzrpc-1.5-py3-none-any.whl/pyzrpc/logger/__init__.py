# -*- encoding: utf-8 -*-
from pyzrpc.logger.logger import _Logger


class Logger(_Logger):

    def logger(self, filename: str): return super().logger(filename)

    def update(self, config: dict): super().update(config)
