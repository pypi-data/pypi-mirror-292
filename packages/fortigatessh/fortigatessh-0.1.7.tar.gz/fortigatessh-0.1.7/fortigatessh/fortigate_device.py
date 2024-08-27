#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Nathan Liang

class FortiGateDevice:
    """Represents a FortiGate device with its connection parameters.
    
    Attributes:
        ip (str): The IP address of the FortiGate device.
        user (str): The username for SSH login.
        pwd (str): The password for SSH login.
        port (int): The SSH port, defaults to 22.
    """
    def __init__(self, ip: str, user: str, pwd: str, port: int = 22):
        if not ip or not user:
            raise ValueError("IP address and username must be provided.")
        self.ip = ip
        self.user = user
        self.pwd = pwd
        self.port = port