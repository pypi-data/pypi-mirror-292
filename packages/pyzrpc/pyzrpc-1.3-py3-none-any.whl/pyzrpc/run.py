# -*- encoding: utf-8 -*-

import time
import multiprocessing

from pyzrpc.service import ServiceStart
from pyzrpc.work import WorkStart


class _ServiceRegistry:
    _service_list = []
    _config = None

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def service_list(self):
        return self._service_list

    def registry(self, services):
        self._service_list = services

    def start(self):
        for _service in self.service_list:
            multiprocessing.Process(target=ServiceStart().service_start, args=(_service, self.config,)).start()
            time.sleep(0.5)
            multiprocessing.Process(target=WorkStart().work_start, args=(_service, self.config,)).start()
