# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/3/15 14:31
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : endpoint_api_deploy_job.py
# @Software: PyCharm
"""
import re
from typing import Optional

deploy_endpoint_job_name_regex = \
    re.compile("^workspaces/(?P<workspace_id>.+?)/endpointhubs/(?P<endpoint_hub_name>.+?)/jobs/(?P<local_name>.+?)$")


class DeployEndpointJobName:
    """
    Deploy endpoint job name.
    """
    def __init__(self, workspace_id: str = None, endpoint_hub_name: str = None, local_name: str = None):
        self.workspace_id = workspace_id
        self.endpoint_hub_name = endpoint_hub_name
        self.local_name = local_name


def parse_deploy_endpoint_job_name(name: str) -> Optional[DeployEndpointJobName]:
    """
    Get workspace id, project name and dataset pipeline from pipeline name.
    """
    m = deploy_endpoint_job_name_regex.match(name)
    if m is None:
        return None
    return DeployEndpointJobName(m.group("workspace_id"), m.group("endpoint_hub_name"), m.group("local_name"))