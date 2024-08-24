# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
"""
testing.py
"""
import copy
import json
import time
import os
import cv2
from ray.data import DataContext
import bcelogger
import ray
import numpy as np
from pyarrow import json as pajson
from typing import Optional
from tritonclient.utils import triton_to_np_dtype
from tritonclient import http as http_client

from windmilltrainingv1.client.training_api_dataset import \
    ANNOTATION_FORMAT_COCO, \
    ANNOTATION_FORMAT_IMAGENET, \
    ANNOTATION_FORMAT_CITYSCAPES, \
    ANNOTATION_FORMAT_PADDLECLAS, \
    ANNOTATION_FORMAT_PADDLEOCR, \
    ANNOTATION_FORMAT_PADDLESEG

from .server.config import TritonServerConfig
from .server.local import TritonServerLocal
from .ds_formatter import (
    AnnotationFormatter,
    _update_image_id_byMD5,
    gaeainfer_to_vistudioV1,
)
from .utils import list_stack_ndarray
from .client_factory import TritonClientFactory


def image_preprocess(path: str, d_type):
    """
    Image preprocess
    :param path:
    :param d_type:
    :return:
    """
    frame = cv2.imread(path)
    img_resize = cv2.resize(frame, (1920, 1080))
    org_h, org_w, _ = img_resize.shape
    img_encode = cv2.imencode(".jpg", img_resize)[1]
    return np.frombuffer(img_encode.tobytes(), dtype=d_type)


def infer(model_name, triton_client, image_id, image_path, template_filepath: str = None):
    """
    Infer
    :param model_name:
    :param triton_client:
    :param image_id:
    :param image_path:
    :param template_filepath:
    :return:
    """
    input_metadata, output_metadata, batch_size = (
        triton_client.get_inputs_and_outputs_detail(model_name=model_name)
    )

    file_names = [image_path]
    template_file_names = [template_filepath]
    repeated_image_data = []
    for file_path in file_names:
        img = np.fromfile(file_path, dtype=triton_to_np_dtype(input_metadata[0]["datatype"]))
        repeated_image_data.append(np.array(img))

    batched_image_data = list_stack_ndarray(repeated_image_data)

    meta_json = json.dumps({"image_id": image_id})
    byte_meta_json = meta_json.encode()
    np_meta_json = np.frombuffer(byte_meta_json, dtype="uint8")
    send_meta_json = np.array(np_meta_json)
    send_meta_json = np.expand_dims(send_meta_json, axis=0)

    if template_filepath is not None:
        repeated_tmp_data = []
        for tem_path in template_file_names:
            img = np.fromfile(tem_path, dtype=triton_to_np_dtype(input_metadata[2]["datatype"]))
            repeated_tmp_data.append(np.array(img))

        batched_tmp_data = list_stack_ndarray(repeated_tmp_data)

    # build triton input
    inputs = [
        http_client.InferInput(
            input_metadata[0]["name"],
            list(batched_image_data.shape),
            input_metadata[0]["datatype"],
        ),
        http_client.InferInput(
            input_metadata[1]["name"],
            send_meta_json.shape,
            input_metadata[1]["datatype"],
        ),
    ]

    if template_filepath is not None:
        inputs.append(http_client.InferInput(
            input_metadata[2]["name"],
            batched_tmp_data.shape,
            input_metadata[2]["datatype"],
        ))
    inputs[0].set_data_from_numpy(batched_image_data, binary_data=False)
    inputs[1].set_data_from_numpy(send_meta_json)
    if template_filepath is not None:
        inputs[2].set_data_from_numpy(batched_tmp_data, binary_data=False)
    # build triton output
    output_names = [output["name"] for output in output_metadata]
    outputs = []
    for output_name in output_names:
        outputs.append(http_client.InferRequestedOutput(output_name, binary_data=True))

    # infer
    result = triton_client.model_infer(model_name, inputs, outputs=outputs)
    # print detailed output
    output_dict = {}
    for output_name in output_names:
        try:
            output_dict[output_name] = eval(result.as_numpy(output_name))
        except Exception as e:
            output_dict[output_name] = json.loads(
                result.as_numpy(output_name).tobytes()
            )

    return output_dict["skill_out_json"]


def evaluate(
    model_path: str,
    dataset_path: str,
    output_uri: str,
    annotation_format: str = "COCO",
    model_name: str = "ensemble",
    triton_server_extra_args: Optional[dict] = None,
    metric=None,
):
    """
    Testing
    :param triton_server_extra_args:
    :param metric:
    :param model_path:
    :param model_name:
    :param dataset_path:
    :param output_uri:
    :param annotation_format:
    :return:
    """
    DataContext.get_current().enable_tensor_extension_casting = False
    triton_server_extra_args["model-repository"] = model_path
    triton_server_extra_args["allow-auth"] = "false"

    triton_server_config = TritonServerConfig().update_config(
        params=triton_server_extra_args
    )

    triton_instance = TritonServerLocal(config=triton_server_config)
    triton_instance.start()

    current_time = time.time()
    start_time = time.time()
    while current_time - start_time <= 5 * 60:
        if triton_instance.is_ready():
            break
        time.sleep(5)
        current_time = time.time()
    if not triton_instance.is_ready():
        raise RuntimeError("Triton server start failed.")

    triton_client = TritonClientFactory.create_http_client(
        server_url=triton_instance.http_base_uri,
        verbose=False,
    )

    delimiter = "\t"
    if annotation_format == ANNOTATION_FORMAT_COCO:
        block_size = 100 << 20
        ds = ray.data.read_json(
            paths=[dataset_path + "/val.json"],
            parse_options=pajson.ParseOptions(newlines_in_values=True),
            read_options=pajson.ReadOptions(block_size=block_size),
        )
        label_ds = ds.flat_map(lambda row: row["categories"])
        labels = label_ds.to_pandas().to_dict(orient="records")

        image_ds = ds.flat_map(lambda row: row["images"])
        file_name_df = image_ds.to_pandas()
        file_name_df.drop_duplicates(subset=["file_name"], inplace=True)
        image_ds = ray.data.from_pandas(file_name_df)
        image_ds = image_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        images = image_ds.to_pandas().to_dict(orient="records")
    elif annotation_format == ANNOTATION_FORMAT_IMAGENET or annotation_format == ANNOTATION_FORMAT_PADDLECLAS:
        ds = ray.data.read_text(paths=[dataset_path + "/val.txt"])

        labels = json.load(open(dataset_path + "/labels.json", "r"))
        image_ds = ds.map(lambda row: {"file_name": row["text"].rsplit(" ", 1)[0]})
        image_ds = image_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        images = image_ds.to_pandas().to_dict(orient="records")
    elif annotation_format == ANNOTATION_FORMAT_CITYSCAPES or annotation_format == ANNOTATION_FORMAT_PADDLESEG:
        ds = ray.data.read_text(paths=[dataset_path + "/val.txt"])

        labels = json.load(open(dataset_path + "/labels.json", "r"))
        image_ds = ds.map(lambda row: {"file_name": row["text"].rsplit(" ", 1)[0]})
        image_ds = image_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        images = image_ds.to_pandas().to_dict(orient="records")
    elif annotation_format == ANNOTATION_FORMAT_PADDLEOCR:
        ds = ray.data.read_text(paths=[dataset_path + "/val.txt"])

        try:
            _, _ = ds.take(1)[0]["text"].split(delimiter, 1)
        except:
            delimiter = " "

        labels = [{"id": "0", "name": "文字"}]
        image_ds = ds.map(lambda row: {"file_name": row["text"].split(delimiter, 1)[0]})

        image_ds = image_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        images = image_ds.to_pandas().to_dict(orient="records")
    else:
        raise ValueError(f"annotation_format should be one of "
                         f"COCO|ImageNet|PaddleClas|PaddleSeg|Cityscapes|PaddleOCR, "
                         f"but got {annotation_format}")

    formatter = AnnotationFormatter(annotation_format=annotation_format, labels=labels, delimiter=delimiter)
    references = formatter.fit(ds).stats_
    references = references.to_pandas().to_dict(orient="records")
    if annotation_format == "Cityscapes" or annotation_format == "PaddleSeg":
        references_copy = copy.deepcopy(references)
        for reference in references_copy:
            reference.pop("annotations")
        images = references_copy

    infer_raw = []
    interval = 50
    for idx, image in enumerate(image_ds.iter_rows()):
        if idx % interval == 0:
            bcelogger.info(f"The {idx} image start infer.")
        template_filepath = \
            os.path.splitext(image["file_name"])[0] + "_template" + os.path.splitext(image["file_name"])[1]
        if os.path.exists(template_filepath):
            infer_dict = infer(model_name, triton_client, image["image_id"], image["file_name"], template_filepath)
        else:
            infer_dict = infer(model_name, triton_client, image["image_id"], image["file_name"])
        infer_raw.append(infer_dict[0])

    predictions = gaeainfer_to_vistudioV1(infer_raw, model_name)

    metric.set_images(images=images)
    metric.set_labels(labels=labels)
    metric(predictions=predictions, references=references, output_uri=output_uri)

    triton_instance.stop()
