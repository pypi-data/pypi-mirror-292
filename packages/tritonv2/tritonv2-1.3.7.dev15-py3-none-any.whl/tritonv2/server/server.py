# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
server.py
"""
from abc import ABC, abstractmethod


class TritonServer(ABC):
    """
    Defines the interface for the objects created by
    TritonServerFactory
    """

    @abstractmethod
    def start(self, env=None):
        """
        Starts the tritonserver

        Parameters
        ----------
        env: dict
            The environment to set for this tritonserver launch
        """

    @abstractmethod
    def stop(self):
        """
        Stops and cleans up after the server
        """

    def update_config(self, params):
        """
        Update the server's arguments

        Parameters
        ----------
        params: dict
            keys are argument names and values are their values.
        """

        self._server_config.update_config(params)

    def config(self):
        """
        Returns
        -------
        TritonServerConfig
            This server's config
        """

        return self._server_config
