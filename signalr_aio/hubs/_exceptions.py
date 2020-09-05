#!/usr/bin/env python
class UnhandledMethodError(Exception):
    def __init__(self, rcv_method, rcv_message, message):
        self.rcv_message = rcv_message
        self.rcv_method = rcv_method
        self.message = message
    pass
