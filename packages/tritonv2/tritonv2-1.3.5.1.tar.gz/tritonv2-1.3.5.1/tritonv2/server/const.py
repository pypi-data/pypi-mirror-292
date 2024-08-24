# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
server.py
"""
ENV_LD_LIBRARY_PATH = (
    "/usr/local/cuda/compat/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:"
    "/opt/tritonserver/lib"
)
ENV_PATH = (
    "/opt/tritonserver/bin:/usr/local/mpi/bin:"
    "/usr/local/nvidia/bin:/usr/local/cuda/bin:"
    "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/ucx/bin"
)

INIT_ENV = {
    "LD_LIBRARY_PATH": ENV_LD_LIBRARY_PATH,
    "PATH": ENV_PATH,
}
