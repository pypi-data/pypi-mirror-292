# -*- encoding: utf-8 -*-
try:
    import eventlet
    eventlet.monkey_patch()
except OSError:
    pass

import os
import errno
import signal
from nameko.runners import ServiceRunner

from pyzrpc.meta import CONFIG_MONGO_FIELD_NAME_KEY, CONFIG_MONGO_FIELD_SERVICE_IPADDR_KEY, \
    CONFIG_MONGO_FIELD_SERVICE_VERSION_KEY, CONFIG_MONGO_FIELD_SERVICE_NAME_KEY, \
    CONFIG_MONGO_FIELD_SERVICE_PID_KEY, CONFIG_MONGO_FIELD_SERVICE_FUNCTIONS_KEY

from pyzrpc.observer import Observer
from pyzrpc.logger import Logger
from pyzrpc.utils import RpcProxy
from pyzrpc.mongo import DBServices

from pyzrpc.service.service_constructor import ServiceBuild


def _container_run(services, config):
    service_runner = ServiceRunner(config)
    for service_cls in services:
        service_runner.add_service(service_cls)

    def shutdown(signum, frame):
        eventlet.spawn_n(service_runner.stop)

    signal.signal(signal.SIGTERM, shutdown)

    service_runner.start()

    running = eventlet.spawn(service_runner.wait)

    while True:
        try:
            running.wait()
        except OSError as exc:
            if exc.errno == errno.EINTR:
                continue
            raise
        except KeyboardInterrupt:
            print()
            try:
                service_runner.stop()
            except KeyboardInterrupt:
                print()
                service_runner.kill()
        else:
            break


class _ServiceStart:

    @staticmethod
    def service_start(service, config):
        _observer = Observer()

        _logger = Logger()
        _rpc_proxy = RpcProxy()
        _mongo = DBServices()

        _observer.config = config
        _observer.attach(_logger)
        _observer.attach(_rpc_proxy)
        _observer.attach(_mongo)
        _observer.notify()

        build = ServiceBuild()
        _cls = build.build(cls_path=service.__file__, rpc_proxy=_rpc_proxy, logger=_logger)

        _logger.logger(_cls.service_name).info('service running : {}'.format(_cls.name))

        _mongo.update_many(
            query={
                CONFIG_MONGO_FIELD_NAME_KEY: _cls.name,
                CONFIG_MONGO_FIELD_SERVICE_IPADDR_KEY: _cls.service_ipaddr
            },
            update_data={
                CONFIG_MONGO_FIELD_NAME_KEY: _cls.name,
                CONFIG_MONGO_FIELD_SERVICE_IPADDR_KEY: _cls.service_ipaddr,
                CONFIG_MONGO_FIELD_SERVICE_NAME_KEY: _cls.service_name,
                CONFIG_MONGO_FIELD_SERVICE_VERSION_KEY: _cls.service_version,
                CONFIG_MONGO_FIELD_SERVICE_PID_KEY: os.getpid(),
                CONFIG_MONGO_FIELD_SERVICE_FUNCTIONS_KEY: _cls.functions
            },
            upsert=True
        )

        _container_run(services=[_cls], config=_rpc_proxy.rpc_config)
