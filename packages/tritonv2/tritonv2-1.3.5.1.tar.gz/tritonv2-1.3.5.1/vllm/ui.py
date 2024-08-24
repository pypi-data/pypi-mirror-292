# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
"""
vllm chat ui example
"""
import gradio as gr
import client

c = client.VLLMClient(endpoint="http://10.211.18.203:8000")


def inference(message, *args):
    """
    inference with vllm
    """
    output = c.streaming_text_generation(prompt=message, max_tokens=3000)
    for h in output:
        for _, line in enumerate(h):
            yield line


gr.ChatInterface(
    inference,
    chatbot=gr.Chatbot(height=800),
    textbox=gr.Textbox(placeholder="Chat with me!", container=False, scale=7),
    description="This is the demo for Gradio UI consuming vllm endpoint with LLM.",
    title="Gradio 🤝 vllm",
    examples=["Are tomatoes vegetables?"],
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
).queue().launch()
