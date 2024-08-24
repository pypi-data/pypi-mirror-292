# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
"""Example Python client for openai"""

import argparse
from openai import OpenAI

def completion(endpoint, prompt, n=10, stream=False):
    """
    生成基于OpenAI API的提示文本生成完成。
    
    Args:
      endpoint: str，目标API服务器地址。
      prompt: str，输入提示文本。
      n: int，返回结果中包含的示例数量。默认为10个。
      stream: bool，是否以流模式返回。默认为False。
      
    Returns: 
      completion：返回类型为str或List[dict]。
        如果`stream`为True，则返回一个迭代器对象；
        否则，返回一个列表。
        
    """
    client = OpenAI(
        api_key="EMPTY",
        base_url=f"http://{endpoint}/v1",
    )

    models = client.models.list()
    model = models.data[0].id

    completion = client.completions.create(
        model=model,
        prompt=prompt,
        echo=False,
        n=n,
        stream=stream,
        logprobs=3
    )
    print("Completion results:")
    if stream:
        for c in completion:
            print(c)
    else:
        print(completion)

def chatcompletion(endpoint):
    """使用OpenAI API生成聊天文本。
    
    Args:
        endpoint (str): OpenAI API的端点地址，格式为`https://<region>.api.openai.com`。
    
    Returns:
        dict: 生成的聊天文本结果，包含`text`字段表示生成的聊天文本内容，`choices`字段表示聊天文本可能的选择列表。
    
    """
    client = OpenAI(
        api_key="EMPTY",
        base_url=f"http://{endpoint}/v1",
    )

    models = client.models.list()
    model = models.data[0].id

    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": "You are a helpful assistant."
        }, {
            "role": "user",
            "content": "Who won the world series in 2020?"
        }, {
            "role":
            "assistant",
            "content":
            "The Los Angeles Dodgers won the World Series in 2020."
        }, {
            "role": "user",
            "content": "Where was it played?"
        }],
        model=model,
    )

    print("Chat completion results:")
    print(chat_completion)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", type=str, default="10.211.18.203:8000")
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--prompt", type=str, default="San Francisco is a")
    parser.add_argument("--stream", type=bool, default=True)
    args = parser.parse_args()
    prompt = args.prompt
    n = args.n
    stream = args.stream
    endpoint = args.endpoint

    print(f"Prompt: {prompt!r}\n", flush=True)
    
    completion(endpoint, prompt, n, stream)
    chatcompletion(endpoint)
    
