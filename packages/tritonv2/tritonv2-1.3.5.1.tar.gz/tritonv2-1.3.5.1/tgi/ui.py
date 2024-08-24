# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
"""
tgi chat ui example
"""


import gradio as gr
from client import TGIClient

endpoint_uri = "http://10.211.18.203:8312/ep-vtqpfbrg"
c = TGIClient(endpoint=endpoint_uri)


def inference(message, *args):
    """
    inference with tgi
    """
    output = c.streaming_text_generation(prompt=message, max_tokens=1000)
    for h in output:
        for _, line in enumerate(h):
            yield line


gr.ChatInterface(
    inference,
    chatbot=gr.Chatbot(height=800),
    textbox=gr.Textbox(placeholder="Chat with me!", container=False, scale=7),
    description="This is the demo for Gradio UI consuming TGI endpoint with LLM.",
    title="Gradio 🤝 TGI",
    examples=["Are tomatoes vegetables?"],
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
).queue().launch()
