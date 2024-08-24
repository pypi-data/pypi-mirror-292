# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/3/15 14:31
# @Author : chujianfei
"""
import re
from typing import Optional

endpoint_name_regex = \
    re.compile(
        "^workspaces/(?P<workspace_id>.+?)/endpointhubs/(?P<endpoint_hub_name>.+?)/endpoints/(?P<local_name>.+?)$")


class EndpointName:
    """
     endpoint  name.
    """

    def __init__(self, workspace_id: str = None, endpoint_hub_name: str = None, local_name: str = None):
        self.workspace_id = workspace_id
        self.endpoint_hub_name = endpoint_hub_name
        self.local_name = local_name


def parse_endpoint_name(name: str) -> Optional[EndpointName]:
    """
    Get workspace id, endpoint hub name and endpoint local name from endpoint name.
    """
    m = endpoint_name_regex.match(name)
    if m is None:
        return None
    return EndpointName(m.group("workspace_id"), m.group("endpoint_hub_name"), m.group("local_name"))
