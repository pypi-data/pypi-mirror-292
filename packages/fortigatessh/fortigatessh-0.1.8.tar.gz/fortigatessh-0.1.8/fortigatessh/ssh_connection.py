#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Nathan Liang

import atexit
import logging
import paramiko
from paramiko_expect import SSHClientInteraction
from .exceptions import SSHConnectionError
from .fortigate_device import FortiGateDevice
from typing import Optional
import traceback as tb
import os

class SSHConnectionManager:
    """Manages SSH connections to a FortiGate device.

    Attributes:
        device (FortiGateDevice): The device to connect to.
        timeout (int): Timeout for SSH operations.
        logger (Optional[logging.Logger]): Logger for output, creates a default logger if not provided.
        log_level (Optional[int]): The logging level for the built-in logger. Defaults to INFO if not provided.
        log_file (Optional[str]): File path to record the entire SSH session.
    """
    def __init__(self, device: FortiGateDevice, logger: Optional[logging.Logger] = None, timeout: int = 10, log_level: Optional[int] = None, log_file: Optional[str] = None):
        self.device = device
        self.timeout = timeout
        if logger is None:
            log_level = log_level or logging.INFO  # Use INFO as default if log_level is not provided
            self.logger = self._create_default_logger(log_level)
        else:
            self.logger = logger
        
        # Initialize session log file
        if log_file:
            self.session_log_file = open(log_file, 'w')
        else:
            self.session_log_file = None
        
        self.client = None
        self.interaction = None
        atexit.register(self.close_connection)

    def _create_default_logger(self, log_level: int) -> logging.Logger:
        """Creates a default logger if none is provided."""
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
            )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def __enter__(self):
        """Supports the use of the 'with' statement."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensures that the connection is closed when exiting the 'with' block."""
        if exc_type:
            self.logger.error(f'Exception in with block: {exc_type}, {exc_value}')
            formatted_traceback = ''.join(tb.format_tb(traceback))
            self.logger.error(f'Traceback details:\n{formatted_traceback}')
        self.close_connection()

    def connect(self):
        """Establishes an SSH connection to the FortiGate device."""
        try:
            self.logger.debug(f'Connecting to {self.device.ip}:{self.device.port}')
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.device.ip, self.device.port, self.device.user, self.device.pwd, timeout=self.timeout)
            self.logger.debug(f'Connected to {self.device.ip}:{self.device.port}')
            self.interaction = SSHClientInteraction(self.client, timeout=self.timeout, output_callback=self._log_output, newline='\n', display=True)
        except paramiko.AuthenticationException:
            raise SSHConnectionError(f"Authentication failed when connecting to {self.device.ip}")
        except paramiko.SSHException as e:
            raise SSHConnectionError(f"SSH error occurred when connecting to {self.device.ip}: {e}")
        except Exception as e:
            raise SSHConnectionError(f"Unexpected error occurred when connecting to {self.device.ip}: {e}")

    def is_connected(self) -> bool:
        """Checks if the SSH connection is still active."""
        return self.client and self.client.get_transport() and self.client.get_transport().is_active()

    def close_connection(self):
        """Ensures the SSH connection is closed cleanly."""
        try:
            if self.client and self.client.get_transport() and self.client.get_transport().is_active():
                self.client.close()
                self.logger.debug(f'Connection to {self.device.ip}:{self.device.port} closed.')
            if self.session_log_file:
                self.session_log_file.close()
        except Exception as e:
            self.logger.error(f'Failed to close connection: {e}')
            raise SSHConnectionError(f"Error closing connection: {e}")

    def _log_output(self, msg: str) -> None:
        """Logs the output from the SSH interaction."""
        self.logger.debug(msg)
        if self.session_log_file:
            self.session_log_file.write(msg + os.linesep)
            self.session_log_file.flush()
