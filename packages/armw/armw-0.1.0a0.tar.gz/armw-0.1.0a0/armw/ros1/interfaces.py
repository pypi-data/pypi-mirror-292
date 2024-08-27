"""
Functions to handle importing interface definitions
"""

import importlib

import roslib.message


def import_message(package_name: str, message_name: str):
    return getattr(importlib.import_module(f"{package_name}.msg"), message_name)


def import_service_(package_name: str, service_name: str):
    service_class = getattr(importlib.import_module(f"{package_name}.srv"), service_name)
    service_request = getattr(importlib.import_module(f"{package_name}.srv"), f"{service_name}Request")
    service_response = getattr(importlib.import_module(f"{package_name}.srv"), f"{service_name}Response")

    return service_class, service_response, service_request


def deserialze_anymsg(msg_data):
    topic_type = msg_data._connection_header['type']
    topic_class = roslib.message.get_message_class(topic_type)
    msg = topic_class()
    msg.deserialize(msg_data._buff)
    return msg
