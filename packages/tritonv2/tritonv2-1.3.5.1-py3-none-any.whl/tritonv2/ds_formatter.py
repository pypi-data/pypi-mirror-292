# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
"""
formatter.py
"""
import datetime
import hashlib
import json
import pandas as pd
import ray
import cv2
from ray.data import Preprocessor, Dataset
import numpy as np
from typing import Sequence

from windmilltrainingv1.client.training_api_dataset import \
    ANNOTATION_FORMAT_COCO, \
    ANNOTATION_FORMAT_IMAGENET, \
    ANNOTATION_FORMAT_CITYSCAPES, \
    ANNOTATION_FORMAT_PADDLECLAS, \
    ANNOTATION_FORMAT_PADDLEOCR, \
    ANNOTATION_FORMAT_PADDLESEG

time_pattern = "%Y-%m-%dT%H:%M:%SZ"


def _update_image_id_byMD5(df: pd.DataFrame) -> "pd.Series":
    """
    update image_id = MD5(row(file_name))
    :param row:
    :return:
    """
    df["image_id"] = df["file_name"].apply(
        lambda x: hashlib.md5(x.encode()).hexdigest()
    )
    image_id_series = df["image_id"].rename("image_id")
    return image_id_series


class AnnotationFormatter(Preprocessor):
    """
    AnnotationFormatter
    """

    def __init__(self, annotation_format, artifact_name: str = "", labels: list = [], delimiter: str = ' '):
        """
        constructor
        :param annotation_format:
        :param artifact_name:
        """
        self._is_fittable = True
        self._annotation_format = annotation_format
        self._artifact_name = artifact_name
        self.labels = labels
        self.delimiter = delimiter

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return:
        """
        if self._annotation_format == ANNOTATION_FORMAT_COCO:
            final_anno_ds = self._fit_coco(ds)
        elif self._annotation_format == ANNOTATION_FORMAT_IMAGENET or \
                self._annotation_format == ANNOTATION_FORMAT_PADDLECLAS:
            final_anno_ds = self._fit_imagenet(ds)
        elif self._annotation_format == ANNOTATION_FORMAT_CITYSCAPES or \
                self._annotation_format == ANNOTATION_FORMAT_PADDLESEG:
            final_anno_ds = self._fit_cityscapes(ds)
        elif self._annotation_format == ANNOTATION_FORMAT_PADDLEOCR:
            final_anno_ds = self._fit_paddleocr(ds)
        else:
            raise ValueError(f"annotation_format should be one of "
                             f"COCO|ImageNet|PaddleClas|PaddleSeg|Cityscapes|PaddleOCR, "
                             f"but got {self._annotation_format}")

        self.stats_ = final_anno_ds
        return self

    def _group_by_image_id(self, group: pd.DataFrame) -> pd.DataFrame:
        """
        group by image_id
        :param group:
        :return:
        """
        image_id = group["image_id"][0]
        ids = group["id"].tolist()
        annotations = list()
        for i in range(len(ids)):
            id = ids[i]
            bbox = group["bbox"].tolist()[i]
            segmentation = group["segmentation"].tolist()[i]
            area = group["area"].tolist()[i]
            cate = group["category_id"].tolist()[i]
            is_crowd = group["iscrowd"].tolist()[i]
            anno = {
                "id": id,
                "bbox": bbox,
                "segmentation": segmentation,
                "area": area,
                "labels": [{"id": cate, "confidence": 1}],
                "iscrowd": is_crowd,
            }
            annotations.append(anno)

        annotation_res = {
            "image_id": image_id,
            "created_at": datetime.datetime.utcnow().strftime(time_pattern),
            "annotations": [annotations],
            "doc_type": "annotation",
            "task_kind": "Manual",
            "artifact_name": self._artifact_name,
            "image_created_at": datetime.datetime.utcnow().strftime(time_pattern),
        }
        return pd.DataFrame(annotation_res)

    def _fit_imagenet(self, ds: "Dataset") -> "Dataset":
        image_ds = ds.map(
            lambda row: {
                "file_name": row["text"].rsplit(" ", 1)[0],
                "text": row["text"],
            }
        )
        image_ds = image_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        images = image_ds.to_pandas().to_dict(orient="records")

        anno_id = 1
        for image in images:
            filepath, label_id = image["text"].rsplit(" ", 1)
            labels = [{"id": label_id, "confidence": 1}]

            annotation = {
                "id": anno_id,
                "labels": labels,
            }
            anno_id += 1

            image["annotations"] = [annotation]

        annotation_ds = ray.data.from_pandas(pd.DataFrame(images))

        return annotation_ds

    def _fit_paddleocr(self, ds: "Dataset") -> "Dataset":
        image_ds = ds.map(
            lambda row: {
                "file_name": row["text"].split(self.delimiter, 1)[0],
                "text": row["text"],
            }
        )

        image_ds = image_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        images = image_ds.to_pandas().to_dict(orient="records")

        anno_id = 1
        for image in images:
            annotations = []
            text = image.get("text")
            filepath, label = text.split(self.delimiter, 1)
            try:
                label = label.replace("'", '"')
                label = json.loads(label)
                if not isinstance(label, Sequence):
                    annotation = {
                        "id": anno_id,
                        "ocr": {"word": label, "confidence": 1},
                        "labels": [{"id": "1", "confidence": 1}],
                    }
                    anno_id += 1

                    image["annotations"] = [annotation]
                    continue
                for l in label:
                    annotation = {"id": anno_id,
                                  "labels": [{"id": "1", "confidence": 1}],
                                  "quadrangle": [point for item in l["points"] for point in item]}
                    annotations.append(annotation)
                    anno_id += 1

                image["annotations"] = annotations
            except json.JSONDecodeError:
                annotation = {
                    "id": anno_id,
                    "ocr": {"word": label, "confidence": 1},
                    "labels": [{"id": "0", "confidence": 1}],
                }
                anno_id += 1

                image["annotations"] = [annotation]

        annotation_ds = ray.data.from_pandas(pd.DataFrame(images))

        return annotation_ds

    def _fit_cityscapes(self, ds: "Dataset") -> "Dataset":
        image_ds = ds.map(
            lambda row: {
                "file_name": row["text"].rsplit(" ", 1)[0],
                "text": row["text"],
            }
        )
        image_ds = image_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        images = image_ds.to_pandas().to_dict(orient="records")

        anno_id = 1
        for image in images:
            filepath, labelpath = image["text"].rsplit(" ", 1)
            label_raw = cv2.imread(labelpath, cv2.IMREAD_GRAYSCALE)
            height, width = label_raw.shape
            image["width"] = width
            image["height"] = height
            image["annotations"] = []
            for label in self.labels:
                label_id = int(label["id"])
                if label_id == 0:
                    continue
                mask = label_raw == label_id
                if not np.any(mask):
                    continue
                pixels = mask.flatten()
                pixels = np.concatenate([[0], pixels, [0]])
                runs = np.where(pixels[1:] != pixels[:-1])[0]
                runs = np.concatenate([runs, [pixels.shape[0] - 2]])
                runs[1:] -= runs[:-1]
                # 如果最后一位为0， 去除
                if runs[-1] == 0:
                    runs = runs[:-1]
                rle = runs.tolist()
                annotation = {
                    "id": anno_id,
                    "labels": [{"id": label_id, "confidence": 1}],
                    "rle": {"counts": rle, "size": [width, height]}
                }
                anno_id += 1

                image["annotations"].append(annotation)

        annotation_ds = ray.data.from_pandas(pd.DataFrame(images))

        return annotation_ds

    def _fit_coco(self, ds: "Dataset") -> "Dataset":
        # 展开 images
        image_ds = ds.flat_map(lambda row: row["images"])

        # 展开 annotations
        annotation_ds = ds.flat_map(lambda row: row["annotations"])

        # merge image_ds and annotation_ds on annotation_ds.image_id = image_ds.id
        drop_id_annotation_ds = annotation_ds.drop_columns(cols=["id"])
        image_df = image_ds.to_pandas()
        annotation_df = drop_id_annotation_ds.to_pandas()
        # merged_df = pd.merge(annotation_df, image_df, left_on="image_id", right_on="id")
        # 如果都是空背景，annotation_df为空
        if annotation_df.shape[0] == 0:
            merged_df = pd.concat([image_df,
                                   pd.DataFrame(columns=["image_id", "bbox", "id", "category_id", "iscrowd", "area"])],
                                  sort=False)
        else:
            merged_df = pd.merge(
                image_df, annotation_df, left_on="id", right_on="image_id", how="left"
            )

        bboxs = merged_df["bbox"].tolist()
        segmentation = merged_df["segmentation"].tolist() if "segmentation" in merged_df.columns else [[]] * len(bboxs)
        normal_bbox_list = [
            arr.tolist() if isinstance(arr, np.ndarray) else [] for arr in bboxs
        ]
        normal_segmentation_list = [
            arr.tolist() if isinstance(arr, np.ndarray) else [] for arr in segmentation
        ]
        merged_df["bbox"] = normal_bbox_list
        merged_df["segmentation"] = normal_segmentation_list
        merged_annotation_ds = ray.data.from_pandas(merged_df).drop_columns(
            cols=["image_id"]
        )

        # # update image_id to md5(file_name)
        updated_annotation_ds = merged_annotation_ds.add_column(
            "image_id", lambda df: _update_image_id_byMD5(df)
        )
        dropped_annotation_ds = updated_annotation_ds.drop_columns(
            cols=["file_name", "height", "width"]
        )
        # group by and map_groups
        group_data = dropped_annotation_ds.groupby("image_id")
        group_anno_ds = group_data.map_groups(lambda g: self._group_by_image_id(g))

        return group_anno_ds


def gaeainfer_to_vistudioV1(raw_data, artifact_name):
    """
    Convert GaeaInfer format to VistudioV1 format
    :param raw_data:
    :param artifact_name:
    :return:
    """
    # 初始化annotations列表
    annotations_list = []

    anno_id = 1
    # 为每个image_id处理annotations
    for item in raw_data:
        annotations = []
        image_id = item["image_id"]  # 假设这是一个递增的标识符

        for pred in item["predictions"]:
            bbox = pred["bbox"]
            area = pred["area"]
            quadrangle = pred.get("quadrangle", [])
            ocr = pred.get("ocr", {})
            segmentation = pred.get("segmentation", [])
            labels = [
                {"id": category["id"], "confidence": category["confidence"]}
                for category in pred["categories"]
            ]

            annotation = {
                "id": anno_id,  # 使用image_id作为annotation的id
                "quadrangle": quadrangle,
                "bbox": bbox,
                "segmentation": segmentation,
                "labels": labels,
                "area": area,
                "ocr": ocr
            }
            anno_id += 1
            annotations.append(annotation)

        # 将每个图片的annotations加入到最终列表中
        annotations_list.append(
            {
                "doc_type": "annotation",
                "artifact_name": artifact_name,
                "task_kind": "Model",
                "image_id": image_id,
                "annotations": annotations,
            }
        )

    return annotations_list
