"""
Functions to handle importing interface definitions
"""

import importlib


def import_message(package_name: str, message_name: str):
    return getattr(importlib.import_module(f"{package_name}.msg"), message_name)


def import_service_(package_name: str, service_name: str):
    service_class = getattr(importlib.import_module(f"{package_name}.srv"), service_name)
    return service_class, service_class.Response, service_class.Request


def deserialze_anymsg(msg_data):
    return msg_data
