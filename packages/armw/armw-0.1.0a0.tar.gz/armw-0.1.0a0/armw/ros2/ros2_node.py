"""
ROS2 version
"""

import time
import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy

from armw.base_node import BaseNode
import armw.globals
import armw.ros2.wait_for_message

executor: rclpy.executors.MultiThreadedExecutor = None


class ServiceProxy(object):
    def __init__(self, service_name, service_type, callback_group):
        self._client = armw.NODE().create_client(service_type, service_name, callback_group=callback_group)
        self.service_class = service_type.Request

    # This causes a crash, so I'm going to leave it off
    # def __del__(self):
    #     armw.NODE().destroy_client(self._client)

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            req = args[0]
        else:
            req = self.service_class(**kwargs)

        future = self._client.call_async(req)
        executor.spin_until_future_complete(future)
        return future.result()


class Ros2Node(BaseNode, Node):
    def __init__(self):
        # Run parent constructors
        Node.__init__(self, armw.globals.NODE_NAME, allow_undeclared_parameters=True, automatically_declare_parameters_from_overrides=True)
        BaseNode.__init__(self)

        self.timer_callback_group = MutuallyExclusiveCallbackGroup()
        self.service_callback_group = MutuallyExclusiveCallbackGroup()

        # Need so do some silly stuff to make services work
        self.service_callbacks = {}

    def spin(self):
        timer_period = 1.0 / self.update_rate
        self.timer = self.create_timer(timer_period, self.loop_once, callback_group=self.timer_callback_group)

    def log(self, level: int, message: str):
        if level == -1:
            self.get_logger().debug(message)
        elif level == 0:
            self.get_logger().info(message)
        elif level == 1:
            self.get_logger().warn(message)
        elif level == 2:
            self.get_logger().error(message)
        elif level == 3:
            self.get_logger().fatal(message)

    def log_throttle(self, interval: int, level: int, message: str):
        if level == -1:
            self.get_logger().debug(message, throttle_duration_sec=interval)
        elif level == 0:
            self.get_logger().info(message, throttle_duration_sec=interval)
        elif level == 1:
            self.get_logger().warn(message, throttle_duration_sec=interval)
        elif level == 2:
            self.get_logger().error(message, throttle_duration_sec=interval)
        elif level == 3:
            self.get_logger().fatal(message, throttle_duration_sec=interval)

    def get_name(self):
        return Node.get_name(self)

    def get_namespace(self):
        return Node.get_namespace(self)

    def search_param(self, parameter_name):
        """
        This isn't really a thing in ROS2
        """

        return parameter_name

    def get_param(self, parameter_name, default=None):
        """
        Returns the value for a given parameter name, or None if it can't find it
        """

        if parameter_name[0] == "~":
            parameter_name = parameter_name[1:]
        parameter_name = parameter_name.replace("/", ".")

        try:
            param_value = self.get_parameter(parameter_name).get_parameter_value()
            if param_value.type == 0:  # Parameter not set
                return default
            return rclpy.parameter.parameter_value_to_python(param_value)
        except Exception as e:
            self.log_error(f"Unable to read parameter {parameter_name}: {e}")
            return default

    def set_param(self, parameter_name, value):
        if parameter_name[0] == "~":
            parameter_name = parameter_name[1:]
        parameter_name = parameter_name.replace("/", ".")

        parameter = rclpy.Parameter(parameter_name, rclpy.Parameter.Type.from_parameter_value(value), value)
        self.set_parameters([parameter])

    def fix_topic_name(self, topic):
        if topic[0] == "~":
            topic = self.get_name() + topic[1:]

        return topic

    def publish(self, topic: str, message_type, queue_size=1, latch=False):
        if latch:
            qos = QoSProfile(depth=1, durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)
        else:
            qos = queue_size

        return self.create_publisher(message_type, self.fix_topic_name(topic), qos)

    def subscribe(self, topic: str, message_type, callback, queue_size=1):
        if message_type is None:
            from ros2topic.api import get_msg_class
            message_type = get_msg_class(self, topic, blocking=True)

        return self.create_subscription(message_type, self.fix_topic_name(topic), callback, queue_size)

    def create_service_server(self, name, service_type, callback):
        self.service_callbacks[name] = callback

        return self.create_service(service_type, name, lambda req, resp: self.service_callback(req, resp, name))

    def service_callback(self, request, response, name):
        response = self.service_callbacks[name](request)
        return response

    def create_service_client(self, name: str, service_type):
        # return self.create_client(service_type, name)
        return ServiceProxy(name, service_type, self.service_callback_group)

    def wait_for_message(self, topic_name, topic_type, timeout=None):
        if timeout is None:
            time_to_wait = 100000  # Essentially forever
        else:
            time_to_wait = timeout

        self.log_warn(f"Waiting for message on {topic_name} for {time_to_wait} seconds")

        if topic_type is None:
            from ros2topic.api import get_msg_class
            topic_type = get_msg_class(self, topic_name, blocking=True)

        success, msg = armw.ros2.wait_for_message.wait_for_message(topic_type, self, topic_name, time_to_wait=time_to_wait)

        self.log_warn(f"Got message on {topic_name}")
        return msg

    def wait_for_service(self, service_name, timeout=None):
        """
        This might not work correctly yet
        """

        # Resolve the name
        if service_name[0] != "/":
            service_name = self.get_namespace() + "/" + service_name

        # Wait
        self.log_warn(f"Waiting for service {service_name}")
        while True:
            for service in self.get_service_names_and_types():
                if service[0] == service_name:
                    self.log_warn(f"Got service {service_name}")
                    return
            time.sleep(0.1)


def main(node_class, node_name):
    global executor

    rclpy.init()
    executor = rclpy.executors.MultiThreadedExecutor()

    armw.globals.NODE_NAME = node_name
    armw.globals.NODE = node_class()

    try:
        armw.globals.NODE.spin()
        executor.add_node(armw.globals.NODE)
        executor.spin()
        rclpy.shutdown()
    except KeyboardInterrupt:
        pass

    print(f"{node_name} shutdown")
    raise Exception("Ayy")  # For testing
