# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
"""Example Python client for vllm.entrypoints.api_server"""

import argparse
import json
from typing import Iterable, List

import requests


class VLLMClient:
    """
    VLLMClient 用于调用vllm server的client。
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
                                        delimiter=b"\0"):
            if chunk:
                data = json.loads(chunk.decode("utf-8"))
                output = data["text"]
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
        output = data["text"]
        return output
    

    def __send_http_request(self, prompt: str, max_tokens: int, stream: bool) -> List[str]:
        """
        Send a HTTP request to the model endpoint and receive the generated text.
        
        Args:
            prompt (str): The input prompt for generating text.
            max_tokens (int): The maximum number of tokens to generate.
            stream (bool): Whether or not to send data in a chunked fashion.
        
        Returns:
            list[str]: A list containing all generated texts.
        
        """
        headers = {"User-Agent": "Test Client"}
        pload = {
            "prompt": prompt,
            "n": 4,
            "use_beam_search": True,
            "temperature": 0.0,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        response = requests.post(self.endpoint + '/generate', headers=headers, json=pload, stream=True)
        return response
    

def clear_line(n: int = 1) -> None:
    """清除控制台指定行数的前面的空格
    
    Args:
        n (int): 清除的行数，默认值为1。
    
    Returns:
        None.
    
    """
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for _ in range(n):
        print(LINE_UP, end=LINE_CLEAR, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", type=str, default="10.211.18.203:8000")
    parser.add_argument("--tokens", type=int, default=1000)
    parser.add_argument("--prompt", type=str, default="San Francisco is a")
    parser.add_argument("--stream", type=bool, default=True)
    args = parser.parse_args()
    prompt = args.prompt
    tokens = args.tokens
    stream = args.stream

    print(f"Prompt: {prompt!r}\n", flush=True)

    client = VLLMClient(endpoint=f"http://{args.endpoint}")
    if stream:
        output = client.streaming_text_generation(prompt, tokens)
        num_printed_lines = 0
        for h in output:
            clear_line(num_printed_lines)
            num_printed_lines = 0
            for i, line in enumerate(h):
                num_printed_lines += 1
                print(f"Beam candidate {i}: {line!r}", flush=True)
    else:
        output = client.text_generation(prompt, tokens)
        for i, line in enumerate(output):
            print(f"Beam candidate {i}: {line!r}", flush=True)
