# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
"""
triton client utils
"""
import uuid
import boto3
import shutil
import os
import numpy as np


S3_KIND = "s3"
LOCAL_KIND = "local"


def gen_unique_id():
    """
    Generate unique id
    """
    return str(uuid.uuid4().hex)


def list_stack_ndarray(arrays) -> np.ndarray:
    """
    Convert list of ndarrays to single ndarray with ndims+=1
    """
    lengths = list(
        map(lambda x, a=arrays: a[x].shape[0], [x for x in range(len(arrays))])
    )
    max_len = max(lengths)
    arrays = list(map(lambda a, ml=max_len: np.pad(a, (0, ml - a.shape[0])), arrays))
    for arr in arrays:
        assert arr.shape == arrays[0].shape, "arrays must have the same shape"
    return np.stack(arrays, axis=0)


def parse_model(model_metadata, model_config):
    """
    Check the configuration of a model to make sure it meets the
    requirements for an image classification network (as expected by
    this client)
    """
    input_metadata = model_metadata["inputs"]
    output_metadata = model_metadata["outputs"]

    max_batch_size = None
    if "max_batch_size" in model_config:
        max_batch_size = model_config["max_batch_size"]

    return input_metadata, output_metadata, max_batch_size


class ModelBlobStoreFactory:
    """
    Model BlobStoreFactory
    """

    @staticmethod
    def create(
        kind,
        model_repository,
        aws_access_key_id="",
        aws_secret_access_key="",
        region="bj",
    ):
        """
        create
        :param kind:
        :param model_repository:
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param region:
        :return:
        """
        assert kind in [S3_KIND, LOCAL_KIND], (
            "Param kind must be in `(S3_KIND, LOCAL_KIND)`, but get kind is {}, "
            "you should set kind is one of `(S3_KIND, LOCAL_KIND)".format(kind)
        )
        if model_repository.startswith("s3:"):
            model_repository = model_repository.lstrip("s3://")
        if kind == S3_KIND:
            if model_repository.startswith("http"):
                url_parts = model_repository.split("//")
                endpoint_url = (
                    url_parts[0] + "//" + url_parts[1].split("/", maxsplit=1)[0]
                )
                bucket = url_parts[1].split("/", maxsplit=2)[1]
                path = url_parts[1].split("/", maxsplit=2)[2]
            else:
                endpoint_url = model_repository.split("/", maxsplit=1)[0]
                bucket = model_repository.split("/", maxsplit=2)[1]
                path = model_repository.split("/", maxsplit=2)[2]

            bs = BlobStoreFactory().create(
                kind,
                bucket=bucket,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region=region,
            )
        else:
            if model_repository.startswith("file"):
                url_parts = model_repository.split("//")
                path = url_parts[1]
            else:
                path = model_repository
            bs = BlobStoreFactory().create(kind, "", "")

        return bs, path


class BlobStoreFactory:
    """
    BlobStoreFactory
    """

    @staticmethod
    def create(
        kind,
        bucket,
        endpoint_url,
        aws_access_key_id="",
        aws_secret_access_key="",
        region="bj",
    ):
        """
        create
        :param kind:
        :param bucket:
        :param endpoint_url:
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param region:
        :return:
        """
        assert kind in [S3_KIND, LOCAL_KIND], (
            "Param kind must be in `(S3_KIND, LOCAL_KIND)`, but get kind is {}, "
            "you should set kind is one of `(S3_KIND, LOCAL_KIND)".format(kind)
        )
        if kind == S3_KIND:
            return S3BlobStore(
                bucket, endpoint_url, aws_access_key_id, aws_secret_access_key, region
            )
        else:
            return LocalBlobStore(endpoint_url)


class LocalBlobStore:
    """
    LocalBlobStore
    """

    def __init__(self, prefix_path) -> None:
        self._prefix = prefix_path + "/"

    def exist(self, path):
        """
        file exist
        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            path = self._prefix + path
            return os.path.exists(path)
        except Exception as e:
            print(f"File {path} not exist: {e}")
            return False

    def read_file(self, path):
        """
        read file
        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            path = self._prefix + path
            with open(path, "r") as f:
                data = f.read()
            return data
        except Exception as e:
            print(f"File {path} read error: {e}")
            return None

    def write_file(self, path, data):
        """
        write file
        Args:
            path (_type_): _description_
            data (_type_): _description_
        """
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        with open(self._prefix + path, "w") as f:
            f.write(data)

    def copy(self, source_key, destination_key):
        """
        copy file
        Args:
            source_key (_type_): _description_
            destination_key (_type_): _description_
        """
        shutil.copy(self._prefix + source_key, self._prefix + destination_key)


class S3BlobStore:
    """
    S3BlobStore
    """

    def __init__(
        self, bucket, endpoint_url, aws_access_key_id, aws_secret_access_key, region
    ):
        self._bucket = bucket
        if not endpoint_url.startswith("http"):
            endpoint_url = f"http://{endpoint_url}"
        self._client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            region_name=region,
        )

    def exist(self, path):
        """_summary_
        file exist
        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            self._client.head_object(Bucket=self._bucket, Key=path)
            return True
        except Exception as e:
            print(f"File {path} not exist: {e}")
            return False

    def read_file(self, path):
        """
        read file
        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        response = self._client.get_object(Bucket=self._bucket, Key=path)
        data = response["Body"].read()
        return data.decode("utf-8")

    def write_file(self, path, data):
        """
        write file
        Args:
            path (_type_): _description_
            data (_type_): _description_
        """
        self._client.put_object(Body=data, Bucket=self._bucket, Key=path)

    def copy(self, source_key, destination_key):
        """
        copy file
        Args:
            source_key (_type_): _description_
            destination_key (_type_): _description_
        """
        copy_source = {"Bucket": self._bucket, "Key": source_key}
        self._client.copy_object(
            CopySource=copy_source, Bucket=self._bucket, Key=destination_key
        )

    def list_object(self, prefix):
        """
        list object
        Args:
            prefix (_type_): _description_
        """
        response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]

    def download_file(self, object_key, local_file_path):
        """
        download file
        Args:
            object_key (_type_): _description_
            local_file_path (_type_): _description_
        """
        self._client.download_file(
            Bucket=self._bucket, Key=object_key, Filename=local_file_path
        )
