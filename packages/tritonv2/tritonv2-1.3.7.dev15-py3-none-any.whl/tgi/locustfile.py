# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
"""
tgi benchmark example on locust
"""

from locust import between, task, User
from locust.exception import LocustError
from huggingface_hub import InferenceClient

from typing import Optional
from urllib3 import PoolManager


class TGIUser(User):
    """
    Represents a TGI "user" which is to be spawned and attack the system that is to be load tested.

    The behaviour of this user is defined by its tasks. Tasks can be declared either directly on the
    class by using the :py:func:`@task decorator <locust.task>` on methods, or by setting
    the :py:attr:`tasks attribute <locust.User.tasks>`.

    This class creates a *client* attribute on instantiation which is an TGI client with support
    for keeping a user session between requests.
    """

    abstract = True
    """If abstract is True, the class is meant to be subclassed, and users will not choose this locust during a test"""

    pool_manager: Optional[PoolManager] = None
    """Connection pool manager to use. If not given, a new manager is created per single user."""

    def __init__(self, *args, **kwargs):
        """
        Create a tgi user.
        """
        super().__init__(*args, **kwargs)
        if self.host is None:
            raise LocustError(
                "You must specify the base host. " +
                "Either in the host attribute in the User class, or on the command line using the --host option."
            )

        self.client = InferenceClient(model=self.host)



class InferenceUser(TGIUser):
    """
    Represents a Inference "user" which is to be spawned and attack the system that is to be load tested.
    """
    wait_time = between(10, 30)  # Time between requests in seconds

    @task
    def call_api(self):
        """
        Call the text generation api.
        """
        prompt = "How do you make cheese?"
        max_new_tokens = 1000
        self.client.text_generation(prompt, max_new_tokens=max_new_tokens)