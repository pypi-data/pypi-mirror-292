# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
server.py
"""
import os
import time
from distutils.spawn import find_executable
from subprocess import TimeoutExpired, Popen, STDOUT

import bcelogger
import requests

from .server import TritonServer
from .config import TritonServerConfig
from .const import INIT_ENV


class TritonServerLocal(TritonServer):
    """
    Concrete Implementation of TritonServer interface that runs
    tritonserver locally as as subprocess.
    """

    def __init__(self, server_cmd_path="/opt/tritonserver/bin/tritonserver", config: TritonServerConfig = None):
        """
        Parameters
        ----------
        server_cmd_path  : str
            The absolute path to the tritonserver executable
        config : TritonServerConfig
            the config object containing arguments for this server instance
        """

        self._server_process = None
        self._server_config = config
        self._server_cmd_path = server_cmd_path
        self._http_base_uri = "localhost:8000"

        assert self._server_config[
            "model-repository"
        ], "Triton Server requires --model-repository argument to be set."

    def __getattr__(self, item):
        return f"'{item}' attribute does not exist!"

    def start(self, env=None):
        """
        Starts the tritonserver container locally
        """
        bcelogger.info(f"cmd path {self._server_cmd_path}")
        if self._server_cmd_path is None:
            self._server_cmd_path = find_executable("tritonserver")
        bcelogger.info(f"cmd path {self._server_cmd_path}")

        if self._server_path:
            if self._server_config["http-port"] is not None:
                self._http_base_uri = f"localhost:{self._server_config['http-port']}"

            # Create command list and run subprocess
            cmd = [self._server_cmd_path]
            cmd += self._server_config.to_args_list()

            # Set environment, update with user config env
            triton_env = os.environ.copy()

            if env:
                # Filter env variables that use env lookups
                for variable, value in env.items():
                    if value.find("$") == -1:
                        triton_env[variable] = value
                    else:
                        # Collect the ones that need lookups to give to the shell
                        triton_env[variable] = os.path.expandvars(value)

            if "NVIDIA_VISIBLE_DEVICES" in triton_env:
                triton_env["CUDA_VISIBLE_DEVICES"] = triton_env["NVIDIA_VISIBLE_DEVICES"]
            if "CXPU_VISIBLE_DEVICES" in triton_env:
                triton_env["XPU_VISIBLE_DEVICES"] = "0"

            for k in INIT_ENV:
                if k not in triton_env:
                    triton_env[k] = INIT_ENV[k]

            # Construct Popen command
            bcelogger.info(f"Cmd is {cmd}")
            self._server_process = Popen(
                cmd,
                bufsize=1,
                stderr=STDOUT,
                start_new_session=True,
                universal_newlines=True,
                env=triton_env,
                close_fds=False,
            )

    def stop(self):
        """
        Stops the running tritonserver
        """

        # Terminate process, capture output
        if self._server_process is not None:
            self._server_process.terminate()
            try:
                self._server_process.communicate(
                    timeout=60,
                )
            except TimeoutExpired:
                self._server_process.kill()
                self._server_process.communicate()
            self._server_process = None

    def is_ready(self):
        """
        Check if the server is ready
        """
        try:
            response = requests.get(
                f"http://{self._http_base_uri}/v2/health/ready", timeout=60
            )
            if response.status_code == 200:
                bcelogger.info(f"Server ready: {self._http_base_uri}")
                return True
        except Exception as e:
            bcelogger.info(f"Please Wait, Server not ready: {e}")
        return False

    @property
    def http_base_uri(self):
        """
        Returns the base uri for the server
        :return:
        """
        return self._http_base_uri
