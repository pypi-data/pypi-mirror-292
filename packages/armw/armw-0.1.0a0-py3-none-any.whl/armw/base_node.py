"""
Base node class that contains all the interfaces needed for the abstract middleware
"""

import armw.globals


class BaseNode(object):
    def __init__(self):
        # Set the global node object before we run the rest of the constructor
        armw.globals.NODE = self

        self.update_rate = 1

    def spin(self):
        raise NotImplementedError

    def loop_once(self):
        pass

    def shutdown(self):
        pass

    def log(self, level, message):
        """
        Abstract function to log to console
        :param level: 0 for info, 1 for warn, 2 for error
        :param message: String to log
        :return: None
        """
        raise NotImplementedError

    def log_debug(self, message, *args):
        self.log(-1, message % args)

    def log_info(self, message, *args):
        self.log(0, message % args)

    def log_warn(self, message, *args):
        self.log(1, message % args)

    def log_error(self, message, *args):
        self.log(2, message % args)

    def log_fatal(self, message, *args):
        self.log(3, message % args)

    def log_throttle(self, interval: int, level: int, message: str):
        raise NotImplementedError

    def log_debug_throttle(self, interval, message, *args):
        self.log_throttle(interval, -1, message % args)

    def log_info_throttle(self, interval, message, *args):
        self.log_throttle(interval, 0, message % args)

    def log_warn_throttle(self, interval, message, *args):
        self.log_throttle(interval, 1, message % args)

    def log_error_throttle(self, interval, message, *args):
        self.log_throttle(interval, 2, message % args)

    def get_name(self):
        raise NotImplementedError

    def get_namespace(self):
        raise NotImplementedError

    def search_param(self, parameter_name):
        raise NotImplementedError

    def has_param(self, parameter_name):
        raise NotImplementedError

    def read_param(self, parameter_name):
        """
        Virtual method.
        Override this for each middleware type
        """
        raise NotImplementedError

    def get_param(self, parameter_name, default=None):
        """
        Returns the value for a given parameter name, or None if it can't find it
        """
        raise NotImplementedError

    def set_param(self, parameter_name, value):
        raise NotImplementedError

    def delete_param(self, parameter_name):
        raise NotImplementedError

    def publish(self, topic: str, message_type, queue_size=1, latch=False):
        raise NotImplementedError

    def subscribe(self, topic: str, message_type, callback, queue_size=1):
        raise NotImplementedError

    def create_service_server(self, name: str, service_type, callback):
        raise NotImplementedError

    def create_service_client(self, name: str, service_type):
        raise NotImplementedError

    def wait_for_message(self, topic, message_type, timeout=None):
        raise NotImplementedError

    def wait_for_service(self, name, timeout=None):
        raise NotImplementedError
