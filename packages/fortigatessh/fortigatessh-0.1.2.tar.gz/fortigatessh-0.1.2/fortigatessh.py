#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Nathan Liang

import atexit
import paramiko
from paramiko_expect import SSHClientInteraction
import traceback
import time
import logging
import threading
from typing import Union, List, Optional

__version__ = "0.6.2"

CTRL_C = "\x03"

class SSHConnectionError(Exception):
    """Raised for errors in the SSH connection."""
    def __init__(self, message: str):
        super().__init__(message)
        logging.error(f'SSHConnectionError: {message}')

class SSHCommandTimeoutError(Exception):
    """Raised when an SSH command times out."""
    def __init__(self, message: str):
        super().__init__(message)
        logging.error(f'SSHCommandTimeoutError: {message}')

class SSHPromptError(Exception):
    """Raised when an expected SSH prompt is not found."""
    def __init__(self, message: str):
        super().__init__(message)
        logging.error(f'SSHPromptError: {message}')

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

class SSHConnectionManager:
    """Manages SSH connections to a FortiGate device.

    Attributes:
        device (FortiGateDevice): The device to connect to.
        timeout (int): Timeout for SSH operations.
        logger (Optional[logging.Logger]): Logger for output, creates a default logger if not provided.
    """
    def __init__(self, device: FortiGateDevice, logger: Optional[logging.Logger] = None, timeout: int = 10):
        self.device = device
        self.timeout = timeout
        self.logger = logger or self._create_default_logger()
        self.client = None
        self.interaction = None
        atexit.register(self.close_connection)

    def _create_default_logger(self) -> logging.Logger:
        """Creates a default logger if none is provided."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)  # Set default logging level to DEBUG
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        except Exception as e:
            self.logger.error(f'Failed to close connection: {e}')
            raise SSHConnectionError(f"Error closing connection: {e}")

    def _log_output(self, msg: str) -> None:
        """Logs the output from the SSH interaction."""
        self.logger.debug(msg)

class CommandExecutor:
    """Executes commands on a FortiGate device via SSH.

    Attributes:
        connection_manager (SSHConnectionManager): The SSH connection manager.
        retries (int): Number of retries for command execution.
        prompt_patterns (Optional[List[str]]): Patterns to identify SSH prompts.
    """
    def __init__(self, connection_manager: SSHConnectionManager, retries: int = 3, prompt_patterns: Optional[List[str]] = None):
        self.connection_manager = connection_manager
        self.retries = retries
        self.prompt_patterns = prompt_patterns or [
            r".* (?:\(Interim\))?[\$#] ",
            r".*\(y\/n\)",
            r"\(Press 'a' to accept\):",
            r".* login: ",
            r"Password: "
        ]
        self.connection_manager.interaction.send('\n')
        self._wait_for_prompt()

    def _wait_for_prompt(self, prompt_patterns: Optional[List[str]] = None):
        """Waits for and handles the expected prompt on the FortiGate device."""
        if prompt_patterns is None:
            prompt_patterns = self.prompt_patterns

        self.connection_manager.logger.debug(f'port {self.connection_manager.device.port} Waiting for prompt')
        error_count = 0

        while True:
            self.connection_manager.logger.debug(f"Current interaction output: {self.connection_manager.interaction.current_output}")
            found_index = self.connection_manager.interaction.expect(prompt_patterns, timeout=self.connection_manager.timeout)
            self.connection_manager.logger.debug(f'Found index: {found_index}')
            if found_index == 0:
                self.connection_manager.logger.debug(f"port {self.connection_manager.device.port} Main prompt detected.")
                break
            elif found_index in (1, 2):
                responses = ['y', 'a']
                self.connection_manager.logger.debug(f"port {self.connection_manager.device.port} Detected special prompt. Sending '{responses[found_index-1]}'.")
                self.connection_manager.interaction.send(responses[found_index-1])
            elif found_index == 3:
                self.connection_manager.logger.debug(f"port {self.connection_manager.device.port} Detected 'login:' prompt. Sending username.")
                self.connection_manager.interaction.send(self.connection_manager.device.user)
            elif found_index == 4:
                self.connection_manager.logger.debug(f"port {self.connection_manager.device.port} Detected 'Password:' prompt. Sending password.")
                self.connection_manager.interaction.send(self.connection_manager.device.pwd)
            elif found_index == -1:
                error_count += 1

            if error_count >= 3:
                self.connection_manager.logger.error(f"port {self.connection_manager.device.port} Error count reached 3. Exiting.")
                raise SSHPromptError("Failed to detect prompt after multiple attempts.")

            time.sleep(1)
        
    def run(self, 
            commands: Union[str, List[str]], 
            delay: int = 0, 
            follow_up_command: Optional[str] = None, 
            timeout: int = 0, 
            retries: int = 1, 
            ensure_connection: bool = False) -> Optional[str]:
        """Executes a command on the FortiGate device with optional delay, timeout, retries, and connection ensuring.

        Args:
            commands (Union[str, List[str]]): The command or list of commands to execute.
            delay (int): Delay in seconds before sending the follow-up command, if any.
            follow_up_command (Optional[str]): A command to send immediately after the main command.
            timeout (int): The maximum time to wait for command execution.
            retries (int): Number of times to retry the command if it fails.
            ensure_connection (bool): Whether to ensure the SSH connection is active before executing the command.

        Returns:
            Optional[str]: The output of the command execution.
        """
        if not isinstance(commands, list):
            commands = [commands]

        if ensure_connection and not self.connection_manager.is_connected():
            try:
                self.connection_manager.connect()
                self.connection_manager.logger.info(f'Connected to port {self.connection_manager.device.port} successfully')
                response = self.run('\n')
                response = response.split('\n')[-1].strip()
                self.connection_manager.logger.info(f'The prompt is "{response}"')
            except SSHConnectionError as e:
                self.connection_manager.logger.error(f'Failed to connect to port {self.connection_manager.device.port}: {e}')
                time.sleep(10)
                return None

        output = ""
        for command in commands:
            try:
                self.connection_manager.logger.debug(f"Executing command: {command}")
                self.connection_manager.interaction.send(command)
                
                if delay > 0:
                    self.connection_manager.logger.debug(f"Waiting for {delay} seconds before sending follow-up command")
                    time.sleep(delay)
                    
                if follow_up_command:
                    self.connection_manager.logger.debug(f"Sending follow-up command: {follow_up_command}")
                    self.connection_manager.interaction.send(follow_up_command)

                if timeout > 0:
                    output = self._execute_with_timeout(self._wait_for_prompt, timeout=timeout, retries=retries)
                else:
                    self._wait_for_prompt()
                
                current_output = self.connection_manager.interaction.current_output_clean.strip()
                output += current_output.replace(command, "").strip()
                if follow_up_command:
                    output = output.replace(follow_up_command, "").strip()

            except Exception as e:
                self.connection_manager.logger.error(f"Exception while running command '{command}': {e}")
                raise SSHCommandTimeoutError(f"Command '{command}' failed due to: {e}")

        return output.strip()
    
    def _execute_with_timeout(self, func, *args, timeout: int, retries: int) -> Optional[str]:
        """Executes a function with a timeout and retry mechanism.

        Args:
            func (Callable): The function to execute.
            timeout (int): Maximum time to wait for the function to complete.
            retries (int): Number of times to retry the function if it times out.

        Returns:
            Optional[str]: The result of the function execution, if successful.
        """
        for attempt in range(retries):
            result = [None]

            def target():
                result[0] = func(*args)

            thread = threading.Thread(target=target)
            thread.start()

            thread.join(timeout)
            if thread.is_alive():
                self.connection_manager.logger.debug(f"Attempt {attempt + 1} timed out. Retrying...")
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    self.connection_manager.logger.error(f"Function {func.__name__} timed out after {retries} attempts.")
                    raise SSHCommandTimeoutError(f"Function {func.__name__} timed out after {retries} attempts.")
            else:
                return result[0]
        return None
