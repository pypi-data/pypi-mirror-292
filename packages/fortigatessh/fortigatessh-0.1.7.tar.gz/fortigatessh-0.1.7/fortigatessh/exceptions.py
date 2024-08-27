#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Nathan Liang

import logging

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