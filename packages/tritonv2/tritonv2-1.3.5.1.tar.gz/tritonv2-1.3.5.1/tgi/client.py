# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
"""
tgi client example
"""

import json
import requests
import argparse
from typing import Iterable, List


class TGIClient:
    """
    TGIClient 用于调用tgi server的client。
    """

    def __init__(self, endpoint: str) -> None:
        """
        初始化方法，用于创建 DingTalkClient 实例。

        Args:
            endpoint (str): 请求的接口地址。

        Returns:
            None: 无返回值。

        """
        self.endpoint = endpoint

    def streaming_text_generation(self, prompt: str, max_tokens: int = 1000) -> Iterable[List[str]]:
        """
        通过HTTP请求生成文本。

        Args:
            prompt (str): 生成文本的提示。
            max_tokens (int): 最大令牌数（默认值：1000）。

        Returns:
            Iterable[List[str]]: 返回一个迭代器，每个元素都是生成文本的一个列表。

        """
        response = self.__send_http_request(prompt, max_tokens, True)
        for chunk in response.iter_lines(chunk_size=8192,
                                         decode_unicode=False,
                                         delimiter=b"\n\n"):
            if chunk:
                data = json.loads(chunk.decode("utf-8").strip('data:'))
                output = data["token"]['text']
                yield output

    def text_generation(self, prompt: str, max_tokens: int = 1000) -> List[str]:
        """
        根据给定的提示，生成文本。

        Args:
            prompt (str): 输入的提示字符串。
            max_tokens (int, optional): 生成文本中最大令牌数量。默认为1000。

        Returns:
            List[str]: 返回一个包含生成文本列表的元组。

        """
        response = self.__send_http_request(prompt, max_tokens, False)
        data = json.loads(response.content)
        output = data["generated_text"]
        return output

    def __send_http_request(self, prompt: str, max_tokens: int, stream: bool):
        """
        Send a HTTP request to the model endpoint and receive the generated text.

        Args:
            prompt (str): The input prompt for generating text.
            max_tokens (int): The maximum number of tokens to generate.
            stream (bool): Whether or not to send data in a chunked fashion.

        Returns:
            list[str]: A list containing all generated texts.

        """

        headers = {"Content-Type": "application/json"}

        pload = {
            "inputs": prompt,
            "parameters": {"max_tokens": max_tokens}
        }

        path = "/generate"
        if stream:
            path = "/generate_stream"

        response = requests.post(self.endpoint + path, headers=headers, json=pload, stream=True)

        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", type=str, default="10.211.18.203:8000")
    parser.add_argument("--tokens", type=int, default=200)
    parser.add_argument("--prompt", type=str, default="San Francisco is a")
    parser.add_argument("--stream", type=bool, default=True)
    args = parser.parse_args()
    prompt = args.prompt
    tokens = args.tokens
    stream = args.stream

    print(f"Prompt: {prompt!r}\n", flush=True)

    client = TGIClient(endpoint=f"http://{args.endpoint}")
    if stream:
        output = client.streaming_text_generation(prompt, tokens)
        num_printed_lines = 0
        for h in output:
            num_printed_lines = 0
            for i, line in enumerate(h):
                num_printed_lines += 1
                print(f"Beam candidate {i}: {line!r}", flush=True)
    else:
        output = client.text_generation(prompt, tokens)
        for i, line in enumerate(output):
            print(f"Beam candidate {i}: {line!r}", flush=True)