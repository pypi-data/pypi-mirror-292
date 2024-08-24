# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
config.pbtxt配置文件更新
Authors: wanggaofei(wanggaofei03@baidu.com)
Date:    2023-03-16
"""
# !/usr/bin/env python3


import json
import os
from typing import Any, Dict, List, Optional

from google.protobuf import json_format, text_format
from google.protobuf.descriptor import FieldDescriptor
from tritonclient.grpc import model_config_pb2
import bcelogger

KEY_MAX_BATCH_SIZE = 'max_batch_size'
KEY_DIMS = 'dims'
KEY_INPUT = 'input'
KEY_INPUTS = 'inputs'
KEY_OUTPUT = 'output'
KEY_OPTIMIZATION = 'optimization'
KEY_EXECUTION_ACCELERATORS = 'executionAccelerators'
KEY_CPU_EXECUTION_ACCELERATOR = 'cpuExecutionAccelerator'
KEY_GPU_EXECUTION_ACCELERATOR = 'gpuExecutionAccelerator'
KEY_TYPE = 'type'
KEY_NAME = 'name'
KEY_WIDTH = 'width'
KEY_HEIGHT = 'height'
KEY_ENSEMBLE_SCHEDULING = 'ensembleScheduling'
KEY_STEP = 'step'
KEY_MODEL_NAME = 'modelName'
KEY_PARAMETERS = 'parameters'
KEY_MODEL_VERSION = 'modelVersion'
KEY_INPUT_MAP = 'inputMap'
KEY_OUTPUT_MAP = 'outputMap'
KEY_BACKEND = 'backend'
BACKEND_NAME_BLS = 'bls'
BACKEND_NAME_OP = 'op'
BACKEND_NAME_PYTHON = 'python'
KEY_VERSION = 'version'
KEY_GROUP = 'group'
PBTXT_NAME = 'config.pbtxt'
KEY_WARMUP = 'modelWarmup'
OP_RESIZE = 'resize'
MODEL_NAME_INDEX = 0
MODEL_VERSION_INDEX = 1
KEY_DYNAMIC_BATCHING = 'dynamicBatching'
KEY_PREFERRED_BATCH_SIZE = 'preferredBatchSize'
KEY_BATCH_SIZE = 'batchSize'


class ModelConfig:
    """
    A class that encapsulates all the metadata about a Triton model.
    """

    _default_config_dict: Dict[str, Any] = {}

    def __init__(self, model_config):
        """
        Parameters
        -------
        model_config : protobuf message
        """

        self._model_config = model_config

    def to_dict(self):
        """
            将模型配置转换为字典格式，返回值类型是dict。
        该方法主要用于将模型配置信息序列化成字典格式，以便进行JSON序列化或其他操作。
        
        Args:
            无参数。
        
        Returns:
            dict (dict): 包含模型配置信息的字典，键值对形如{"key": value}。value可以是任意类型，包括int、float、str等。
        """
        model_config_dict = json_format.MessageToDict(self._model_config)
        return model_config_dict

    @classmethod
    def from_dict(cls, model_config_dict):
        """
            从字典中创建模型配置。
        参数:
            model_config_dict (dict): 包含模型配置信息的字典，必须包含以下键值对：
                - "model_name" (str): 模型名称。
                - "pretrained" (bool, optional): 是否使用预训练权重（默认为False）。
                - "weights" (str, optional): 预训练权重文件路径（如果不存在则使用预训练权重）。
                - "num_classes" (int, optional): 类别数量（默认为80）。
                - "backbone" (str, optional): 后端网络名称（默认为'resnet50'）。
                - "input_size" (int, optional): 输入图像大小（默认为224）。
                - "pooling" (str, optional): 池化方式（默认为'avg'）。
                - "interpolation" (str, optional): 插值方式（默认为'bicubic'）。
                - "mean" (list[float], optional): 归一化均值（默认为[0.485, 0.456, 0.406]）。
                - "std" (list[float], optional): 归一化标准差（默认为[0.229, 0.224, 0.225]）。
                - "device" (str, optional): 设备名称（默认为'cuda'）。
        返回值:
            ModelConfig (object): 模型配置实例。
        """
        return ModelConfig.create_from_dictionary(model_config_dict)

    @staticmethod
    def _create_from_file(pbtxt_name):
        """
        Constructs a ModelConfig from the pbtxt at file

        Parameters
        -------
        pbtxt_name : str
            The full path to config.pbtxt

        Returns
        -------
        ModelConfig
        """
        if not os.path.isfile(pbtxt_name):
            raise FileNotFoundError(f'Config file {pbtxt_name} does not exist, '
                                    f'make sure that you have specified the correct model repository and model name')

        with open(pbtxt_name, "r+") as f:
            config_str = f.read()

        protobuf_message = text_format.Parse(config_str, model_config_pb2.ModelConfig())

        return ModelConfig(protobuf_message)

    @staticmethod
    def create_from_dictionary(model_dict):
        """
        Constructs a ModelConfig from a Python dictionary

        Parameters
        -------
        model_dict : dict
            A dictionary containing the model configuration.

        Returns
        -------
        ModelConfig
        """

        protobuf_message = json_format.ParseDict(
            model_dict, model_config_pb2.ModelConfig()
        )

        return ModelConfig(protobuf_message)

    def is_ensemble(self) -> bool:
        """
        Returns
        -------
        bool
           True if this is an ensemble model
        """

        return getattr(self._model_config, "platform") == "ensemble"

    def get_ensemble_composing_step(self) -> Optional[list]:  # [[name, version, in_map, out_map]]
        """
            get model dag by ensemble
        """
        step_models = []
        model_config_dict = self.to_dict()
        for v in model_config_dict[KEY_ENSEMBLE_SCHEDULING][KEY_STEP]:
            name = v[KEY_MODEL_NAME]
            version = v[KEY_MODEL_VERSION]
            input_map = {}
            for key, val in v[KEY_INPUT_MAP].items():
                input_map[key] = val
            output_map = {}
            for key, val in v[KEY_OUTPUT_MAP].items():
                output_map[key] = val
            step_models.append([name, version, input_map, output_map])
        return step_models

    def get_bls_optmization(self):
        """
            get bls dag information
        """
        sub_models = []
        model_config_dict = self.to_dict()

        if KEY_OPTIMIZATION in model_config_dict and \
                KEY_EXECUTION_ACCELERATORS in model_config_dict[KEY_OPTIMIZATION] and \
                KEY_GPU_EXECUTION_ACCELERATOR in model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS]:
            gpu_exec_acc_dag = \
                model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS][KEY_GPU_EXECUTION_ACCELERATOR]
            for v in gpu_exec_acc_dag:
                if KEY_PARAMETERS in v and 'model_name' in v[KEY_PARAMETERS]:
                    nmae = v[KEY_PARAMETERS]['model_name']
                    version = v[KEY_PARAMETERS][KEY_VERSION]
                    in_map = {}
                    out_map = {}
                    for key, val in v[KEY_PARAMETERS].items():
                        if key.startswith('IN'):
                            in_names = val.split(':')
                            in_map[in_names[0]] = in_names[1]  # in/out according to sub-ensemble
                        if key.startswith('OUT'):
                            in_names = val.split(':')
                            out_map[in_names[0]] = in_names[1]  # in/out according to sub-ensemble
                    group_size = v[KEY_PARAMETERS][KEY_GROUP]
                    sub_models.append([nmae, version, in_map, out_map, group_size])
        return sub_models

    def get_shape_by_name(self, name: str) -> Optional[list]:
        """
            get input/output 4-dim shape
        """
        model_config_dict = self.to_dict()
        if 'maxBatchSize' in model_config_dict:
            batch_size = model_config_dict['maxBatchSize']
        else:
            bcelogger.info('maxBatchSize not found. Setting batch size to 0')
            batch_size = 0

        for n in [KEY_INPUT, KEY_OUTPUT]:
            for v in model_config_dict[n]:
                if v[KEY_NAME] == name:
                    dims = v[KEY_DIMS]

                    if batch_size != 0:
                        full_dims = [batch_size]
                        full_dims.extend([int(x) for x in dims])
                        return full_dims
        return []

    def get_ensemble_composing_models(self) -> Optional[List[str]]:
        """
        Returns
        -------
            List[str]: Sub-model names
        """

        if not self.is_ensemble():
            bcelogger.error(
                "Cannot find composing_models. Model platform is not ensemble."
            )

        try:
            composing_models = [
                model["modelName"]
                for model in self.to_dict()[KEY_ENSEMBLE_SCHEDULING][KEY_STEP]
            ]
        except Exception:
            bcelogger.error(
                "Cannot find composing_models. Ensemble Scheduling and/or step is not present in config protobuf."
            )

        return composing_models

    def set_composing_model_variant_name(
            self, composing_model_name: str, variant_name: str
    ) -> None:
        """
        Replaces the Ensembles composing_model's name with the variant name
        """

        if not self.is_ensemble():
            bcelogger.error(
                "Cannot find composing_models. Model platform is not ensemble."
            )

        model_config_dict = self.to_dict()

        try:
            for composing_model in model_config_dict[KEY_ENSEMBLE_SCHEDULING][KEY_STEP]:
                if composing_model["modelName"] == composing_model_name:
                    composing_model["modelName"] = variant_name
        except Exception:
            bcelogger.error(
                "Cannot find composing_models. Ensemble Scheduling and/or step is not present in config protobuf."
            )

        self._model_config = self.from_dict(model_config_dict)._model_config

    def set_model_name(self, model_name: str) -> None:
        """
            设置模型名称。
        
        Args:
            model_name (str): 模型名称，字符串类型。
        
        Returns:
            None: 无返回值，直接修改了当前对象的模型名称。
        """
        model_config_dict = self.to_dict()
        model_config_dict["name"] = model_name
        self._model_config = self.from_dict(model_config_dict)._model_config

    def write_config_to_file(
            self, pbtxt_name
    ):
        """
        Writes a protobuf config file.

        Parameters
        ----------
        pbtxt_name : str
            config.pbtxt file to be saved

        Raises
        ------
        TritonModelAnalyzerException
            If the path doesn't exist or the path is a file
        """

        model_config_bytes = text_format.MessageToBytes(self._model_config)
        # Create current variant model as symlinks to first variant model

        with open(pbtxt_name, "wb") as f:
            f.write(model_config_bytes)

    def get_config(self):
        """
        Get the model config.

        Returns
        -------
        dict
            A dictionary containing the model configuration.
        """

        return json_format.MessageToDict(
            self._model_config, preserving_proto_field_name=True
        )

    def get_config_str(self):
        """
        Get the model config json str

        Returns
        -------
        str
            A JSON string containing the model configuration.
        """
        return json.dumps(self.get_config())

    def set_config(self, config):
        """
        Set the model config from a dictionary.

        Parameters
        ----------
        config : dict
            The new dictionary containing the model config.
        """

        self._model_config = json_format.ParseDict(
            config, model_config_pb2.ModelConfig()
        )

    def set_field(self, name, value):
        """
        Set a value for a Model Config field.

        Parameters
        ----------
        name : str
            Name of the field
        value : object
            The value to be used for the field.
        """
        model_config = self._model_config

        if (
                model_config.DESCRIPTOR.fields_by_name[name].label
                == FieldDescriptor.LABEL_REPEATED
        ):
            repeated_field = getattr(model_config, name)
            del repeated_field[:]
            repeated_field.extend(value)
        else:
            setattr(model_config, name, value)

    def set_input_dims(self, idx, dims):
        """
            set input node dims
        """
        model_config_dict = self.to_dict()
        if KEY_INPUT in model_config_dict:
            for v in model_config_dict[KEY_INPUT]:
                if KEY_DIMS in v and idx + len(dims) <= len(v[KEY_DIMS]):
                    self.set_dict_dims(v, idx, dims)
        self._model_config = self.from_dict(model_config_dict)._model_config

    def _is_nhwc(self, dims: list):
        """
            guess nhwc by last dim value
        """
        return 1 <= int(dims[-1]) <= 6

    def _need_modify_shape(self, dims: list):
        """
            only modify shape w/h
        """
        num = 0
        for d in dims:
            if d == -1:
                num += 1
        return num <= 1

    def set_model_input_warmup_shape(self, in_pin_name: str, width: int, height: int, channel: int,
                                     max_batch_size: int, contain_preprocess: str = None):
        """
            set model input/warmup shape by template
        """
        # 1. get input shape
        model_config_dict = self.to_dict()
        if KEY_INPUT in model_config_dict:
            for v in model_config_dict[KEY_INPUT]:
                if KEY_NAME in v and v[KEY_NAME] == in_pin_name and self._need_modify_shape(v[KEY_DIMS]):
                    if contain_preprocess is not None:
                        if contain_preprocess == "true":
                            v[KEY_DIMS][-1] = channel
                            v[KEY_DIMS][-2] = width
                            v[KEY_DIMS][-3] = height
                        else:
                            v[KEY_DIMS][-1] = width
                            v[KEY_DIMS][-2] = height
                            v[KEY_DIMS][-3] = channel
                    else:
                        # 2. find nhwc/nchw
                        if self._is_nhwc(v[KEY_DIMS]):
                            v[KEY_DIMS][-1] = channel
                            v[KEY_DIMS][-2] = width
                            v[KEY_DIMS][-3] = height
                        else:
                            v[KEY_DIMS][-1] = width
                            v[KEY_DIMS][-2] = height
                            v[KEY_DIMS][-3] = channel
            if KEY_WARMUP in model_config_dict:
                for v in model_config_dict[KEY_WARMUP]:
                    if KEY_BATCH_SIZE in v:
                        v[KEY_BATCH_SIZE] = max_batch_size
                        bcelogger.info('modify warmup batch size to {}'.format(max_batch_size))
                    else:
                        bcelogger.warning('do NOT find warmup batch size')
                    if KEY_INPUTS in v:
                        for key, val in v[KEY_INPUTS].items():
                            if key == in_pin_name:
                                dims = val[KEY_DIMS]
                                if self._is_nhwc(dims):
                                    dims[-1] = channel
                                    dims[-2] = width
                                    dims[-3] = height
                                else:
                                    dims[-1] = width
                                    dims[-2] = height
                                    dims[-3] = channel

        self._model_config = self.from_dict(model_config_dict)._model_config

    def set_output_dims(self, output_name, idx, dims):
        """
            set output node dims
        """
        model_config_dict = self.to_dict()
        if KEY_OUTPUT in model_config_dict:
            for v in model_config_dict[KEY_OUTPUT]:
                if (output_name is None or v[KEY_NAME] == output_name) \
                        and KEY_DIMS in v and max(idx, 0) + len(dims) <= len(v[KEY_DIMS]):
                    if idx < 0:
                        idx = len(v[KEY_DIMS]) + idx
                    self.set_dict_dims(v, idx, dims)
        self._model_config = self.from_dict(model_config_dict)._model_config

    def set_dict_dims(self, config_dict, idx: int, dims: list):
        """
            set array dims
        """
        if KEY_DIMS not in config_dict or len(dims) + idx > len(config_dict[KEY_DIMS]):
            bcelogger.error('do NOT find dims in config or dims invalid. idx: {} dims: {}'.format(idx, dims))
        else:
            config_dict[KEY_DIMS][idx: idx + len(dims)] = dims

    # nodes: op-nodes
    # retrive_nodes: [in_pin_names]
    def _get_resize_op_name(self, nodes: list, retrive_nodes: list):
        """
            get op name in the output-tree
        """
        while True:
            if len(retrive_nodes) <= 0:
                return None

            in_pin_name = retrive_nodes[0][0]
            retrive_nodes[0].remove(in_pin_name)
            if len(retrive_nodes[0]) <= 0:
                retrive_nodes.pop(0)

            for n in nodes:
                if in_pin_name in self._get_op_parameter_out_names(n[KEY_PARAMETERS]):
                    # input pin name is the node's output pint name
                    if n[KEY_PARAMETERS][KEY_TYPE] == OP_RESIZE:
                        retrive_nodes = []
                        return n[KEY_NAME]
                    retrive_item = [n[KEY_NAME]]
                    for key, val in n[KEY_PARAMETERS].items():
                        if key.startswith(KEY_INPUT):
                            retrive_item.append(val)
                    break

    def _get_op_parameter_in_names(self, parameters: dict):
        """
            get op in names
        """
        names = []
        for k, v in parameters.items():
            if k.startswith(KEY_INPUT):
                names.append(v)
        return names

    def _get_op_parameter_out_names(self, parameters: dict):
        """
            get op out names
        """
        names = []
        for k, v in parameters.items():
            if k.startswith(KEY_OUTPUT):
                names.append(v)
        return names

    # output_name -> resize_op_name
    def get_op_resize_output_map(self):
        """
            get output -> resize-op map, used for modify op w/h
        """
        output_name_resize_dict = {}
        # 1. get output names
        output_names = self.get_ouput_names()

        # 2. push output name node in-pin-names
        model_config_dict = self.to_dict()
        if KEY_OPTIMIZATION in model_config_dict and \
                KEY_EXECUTION_ACCELERATORS in model_config_dict[KEY_OPTIMIZATION] and \
                KEY_CPU_EXECUTION_ACCELERATOR in model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS]:
            cpu_exec_acc_dag = \
                model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS][KEY_CPU_EXECUTION_ACCELERATOR]

            for name in output_names:
                for n in cpu_exec_acc_dag:
                    for k, v in n.get(KEY_PARAMETERS, {}).items():
                        if v == name and k.startswith(KEY_OUTPUT):
                            in_names = self._get_op_parameter_in_names(n[KEY_PARAMETERS])
                            resize_name = self._get_resize_op_name(cpu_exec_acc_dag, [in_names])
                            if resize_name is not None:
                                output_name_resize_dict[name] = resize_name

        return output_name_resize_dict

    def set_op_resize_width_height(self, output_name: str, width: int, height: int):
        """
            set all resize-type op width/height
        """
        model_config_dict = self.to_dict()
        if KEY_OPTIMIZATION in model_config_dict and \
                KEY_EXECUTION_ACCELERATORS in model_config_dict[KEY_OPTIMIZATION] and \
                KEY_CPU_EXECUTION_ACCELERATOR in model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS]:
            cpu_exec_acc_dag = \
                model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS][KEY_CPU_EXECUTION_ACCELERATOR]
            for v in cpu_exec_acc_dag:
                if KEY_PARAMETERS in v and KEY_TYPE in v[KEY_PARAMETERS] and KEY_WIDTH in v[KEY_PARAMETERS] and \
                        KEY_HEIGHT in v[KEY_PARAMETERS] and v[KEY_PARAMETERS][KEY_TYPE] == OP_RESIZE:
                    v[KEY_PARAMETERS][KEY_WIDTH] = str(width)
                    v[KEY_PARAMETERS][KEY_HEIGHT] = str(height)
        self._model_config = self.from_dict(model_config_dict)._model_config

    def set_segment_width_height(self, width: int, height: int):
        """
            set segment output w/h
        """
        self.set_output_dims(None, -2, [height, width])

    def delete_output(self, name: str):
        """
         delete output
        """
        model_config_dict = self.to_dict()

        if KEY_OUTPUT in model_config_dict:
            new_output_list = []
            for v in model_config_dict[KEY_OUTPUT]:
                if v[KEY_NAME] != name:
                    new_output_list.append(v)
            model_config_dict[KEY_OUTPUT] = new_output_list

        self._model_config = self.from_dict(model_config_dict)._model_config

    def set_preproc_width_height(self, output_names: list, width: int, height: int, index: int = None):
        """
            set preprocess width/height parameter
        """
        # 1. set output
        for name in output_names:
            if self._is_nhwc(self.get_shape_by_name(name)):
                dims = [height, width]
                idx = -3
            else:
                dims = [width, height]
                idx = -2

            if index is not None:
                idx = index

            self.set_output_dims(name, idx, dims)

            # 2. set resize op
            self.set_op_resize_width_height(name, width, height)

    def modify_output_dim_value(self, pin_names: list, val: int):
        """
        modify dim index 1 value, used for ppyoloe max bbox count
        """
        model_config_dict = self.to_dict()
        if KEY_OUTPUT in model_config_dict:
            self.modify_in_out_dim_value(model_config_dict[KEY_OUTPUT], pin_names, val)
        self._model_config = self.from_dict(model_config_dict)._model_config

    def modify_input_dim_value(self, pin_names: list, val: int):
        """
        modify dim index 1 value, used for ppyoloe max bbox count
        """
        model_config_dict = self.to_dict()

        if KEY_OUTPUT in model_config_dict:
            self.modify_in_out_dim_value(model_config_dict[KEY_INPUT], pin_names, val)
        self._model_config = self.from_dict(model_config_dict)._model_config

    def modify_in_out_dim_value(self, pin_list: list, pin_names: list, val: int):
        """
            set dim index value
        """
        batch_size = self.max_batch_size()
        for pin in pin_list:
            if pin[KEY_NAME] in pin_names:
                idx = 1 if batch_size == 0 else 0
                if pin[KEY_DIMS][idx] != -1:
                    pin[KEY_DIMS][idx] = val

    def modify_model_name(self, names: dict) -> bool:
        """
            set model name & version
        """
        need_save_pb = False
        model_config_dict = self.to_dict()
        # 1. modify name
        if KEY_NAME in model_config_dict:
            if model_config_dict[KEY_NAME] in names:
                model_config_dict[KEY_NAME] = names[model_config_dict[KEY_NAME]][MODEL_NAME_INDEX]
                need_save_pb = True
        else:
            bcelogger.warning('{} do not have {}'.format(PBTXT_NAME, KEY_NAME))

        # 2. modify ensemble step model name & version
        if KEY_ENSEMBLE_SCHEDULING in model_config_dict and KEY_STEP in model_config_dict[KEY_ENSEMBLE_SCHEDULING]:
            for v in model_config_dict[KEY_ENSEMBLE_SCHEDULING][KEY_STEP]:
                if KEY_MODEL_NAME in v and v[KEY_MODEL_NAME] in names:
                    new_name, new_version = names[v[KEY_MODEL_NAME]]
                    bcelogger.info('modify model name {} to {}&{}'.format(v[KEY_MODEL_NAME], new_name, new_version))
                    v[KEY_MODEL_NAME] = new_name
                    v[KEY_MODEL_VERSION] = new_version

                    need_save_pb = True

        # 3. modify bls sub model name
        if KEY_OPTIMIZATION in model_config_dict and \
                KEY_EXECUTION_ACCELERATORS in model_config_dict[KEY_OPTIMIZATION] and \
                KEY_GPU_EXECUTION_ACCELERATOR in model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS]:
            gpu_exec_acc_dag = \
                model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS][KEY_GPU_EXECUTION_ACCELERATOR]
            for v in gpu_exec_acc_dag:
                if KEY_PARAMETERS in v and 'model_name' in v[KEY_PARAMETERS] \
                        and v[KEY_PARAMETERS]['model_name'] in names:
                    v[KEY_PARAMETERS]['model_name'] = names[v[KEY_PARAMETERS]['model_name']][MODEL_NAME_INDEX]
                    need_save_pb = True

        if need_save_pb:
            self._model_config = self.from_dict(model_config_dict)._model_config
        return need_save_pb

    def get_field(self, name):
        """
        Get the value for the current field.
        """

        model_config = self._model_config
        return getattr(model_config, name)

    def max_batch_size(self) -> int:
        """
        Returns the max batch size (int)
        """

        model_config = self.get_config()
        return model_config.get(KEY_MAX_BATCH_SIZE, 0)

    def dynamic_batching_string(self) -> str:
        """
        Returns
        -------
        str
            representation of the dynamic batcher
            configuration used to generate this result
        """

        model_config = self.get_config()
        if "dynamic_batching" in model_config:
            return "Enabled"
        else:
            return "Disabled"

    def modify_dynamic_batching(self, max_batch_size: int):
        """
            modify batch & warmup batch
        """
        model_config_dict = self.to_dict()
        if KEY_DYNAMIC_BATCHING in model_config_dict and \
                KEY_PREFERRED_BATCH_SIZE in model_config_dict[KEY_DYNAMIC_BATCHING]:
            prefer_batchs = []
            need_save = False
            for _, v in enumerate(model_config_dict[KEY_DYNAMIC_BATCHING][KEY_PREFERRED_BATCH_SIZE]):
                if max_batch_size < v:
                    need_save = True
                prefer_batchs.append(min(max_batch_size, v))
            if need_save:
                model_config_dict[KEY_DYNAMIC_BATCHING][KEY_PREFERRED_BATCH_SIZE] = prefer_batchs
                self._model_config = self.from_dict(model_config_dict)._model_config
                bcelogger.info('modify {} to {}'.format(KEY_DYNAMIC_BATCHING, prefer_batchs))
        else:
            bcelogger.info('do NOT have {}.{}'.format(KEY_DYNAMIC_BATCHING, KEY_PREFERRED_BATCH_SIZE))

    def instance_group_count(self, system_gpu_count: int) -> int:
        """
        Returns:
            int: The total number of instance groups (cpu + gpu)
        """

        kind_to_count = self._get_instance_groups(system_gpu_count)
        instance_group_count = sum([count for count in kind_to_count.values()])

        return instance_group_count

    def instance_group_string(self, system_gpu_count: int) -> str:
        """
        Returns
        -------
        str
            representation of the instance group used
            to generate this result

            Format is "GPU:<count> + CPU:<count>"
        """

        kind_to_count = self._get_instance_groups(system_gpu_count)

        ret_str = ""
        for k, v in kind_to_count.items():
            if ret_str != "":
                ret_str += " + "
            ret_str += f"{v}:{k}"
        return ret_str

    def _get_instance_groups(self, system_gpu_count: int) -> Dict[str, int]:
        """
        Returns a dictionary with type of instance (GPU/CPU) and its count
        """
        model_config = self.get_config()

        # TODO change when remote mode is fixed
        default_kind = "CPU"
        default_count = 1

        instance_group_list: List[Dict[str, Any]] = [{}]
        if "instance_group" in model_config:
            instance_group_list = model_config["instance_group"]

        kind_to_count: Dict[str, Any] = {}

        for group in instance_group_list:
            group_kind = default_kind
            group_count = default_count
            group_gpus_count = system_gpu_count
            # Update with instance group values
            if "kind" in group:
                group_kind = group["kind"].split("_")[1]
            if "count" in group:
                group_count = group["count"]
            if "gpus" in group:
                group_gpus_count = len(group["gpus"])

            group_total_count = group_count
            if group_kind == "GPU":
                group_total_count *= group_gpus_count

            if group_kind not in kind_to_count:
                kind_to_count[group_kind] = 0
            kind_to_count[group_kind] += group_total_count

        return kind_to_count

    def get_input_names(self):
        """
            get input names of node
        """
        return self._get_in_out_names(KEY_INPUT)

    def get_ouput_names(self):
        """
            get input names of node
        """
        return self._get_in_out_names(KEY_OUTPUT)

    def _get_in_out_names(self, in_out: str):
        """
            get in/out names of node inner
        """
        model_config = self.get_config()
        names = []
        for n in model_config[in_out]:
            names.append(n[KEY_NAME])
        return names


if __name__ == "__main__":
    max_batch_size = 100
    width = 777
    height = 666
    channel = 3
    # 1. ensemble
    # pbtxt_path = './ensemble.pbtxt'
    # pbtxt = ModelConfig._create_from_file(pbtxt_path)
    # print('is ensemble: {}'.format(pbtxt.is_ensemble()))
    # pbtxt.set_field(KEY_MAX_BATCH_SIZE, max_batch_size)

    # names = {
    #     'ppyoloeplus-preprocess': 'abc-preprocess',
    #     'ppyoloeplus-model': 'abc-model',
    #     'ppyoloeplus-postprocess': 'abc-postprocess',
    # }

    # pbtxt.set_ensemble_step_model_name(names)
    # dst_path = './output_ensemble.pbtxt'
    # pbtxt.write_config_to_file(dst_path)

    # 2. preproc
    pbtxt_path = './preproc.pbtxt'
    pbtxt = ModelConfig._create_from_file(pbtxt_path)
    pbtxt.set_field(KEY_MAX_BATCH_SIZE, max_batch_size)
    pbtxt.modify_dynamic_batching(max_batch_size)

    # pbtxt.set_preproc_width_height(width=width, height=height)
    dst_path = './output_preproc.pbtxt'
    pbtxt.write_config_to_file(dst_path)

    # 3. model
    pbtxt_path = './model.pbtxt'
    pbtxt = ModelConfig._create_from_file(pbtxt_path)

    pbtxt.set_field(KEY_MAX_BATCH_SIZE, max_batch_size)
    # used for ppyoloe
    pbtxt.set_model_input_warmup_shape('image', width, height, channel, max_batch_size)

    max_box_count = 100
    output_pin_names = ['det_boxes', 'det_scores', 'det_classes']
    # pbtxt.modify_output_dim_value(output_pin_names, max_box_count)
    dst_path = './output_model.pbtxt'
    pbtxt.write_config_to_file(dst_path)
