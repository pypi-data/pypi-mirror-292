# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
根据技能包文件夹构建DAG图
- 支持BLS(python/c++)
- 支持sub-ensemble
Authors: wanggaofei(wanggaofei03@baidu.com)
Date:    2023-03-28
"""
import os
import bcelogger
from typing import Any, Dict
from .update_pbtxt import ModelConfig, KEY_NAME, KEY_BACKEND, BACKEND_NAME_BLS, PBTXT_NAME, \
    BACKEND_NAME_OP, KEY_MAX_BATCH_SIZE, BACKEND_NAME_PYTHON
from .python_bls_processor import PythonBLSProcessor

ADV_PARAM_WIDTH = 'width'
ADV_PARAM_HEIGHT = 'height'
ADV_PARAM_CHANNEL = 'channel'
ADV_PARAM_BATCH_SIZE = 'batch_size'
ADV_PARAM_MODEL_TYPE = 'model_type'
ADV_PARAM_MAX_BBOX_COUNT = 'max_bbox_count'
# old_name -> [new_name, new_version]
ADV_PARAM_MODEL_NAME_PAIR = 'model_name_pair'


def get_int_val(advanced_parameters: dict, key: str) -> int:
    """
        get integer value from parameter
    """
    if key not in advanced_parameters.keys():
        return None
    else:
        return int(advanced_parameters[key])


def get_string_val(advanced_parameters: dict, key: str) -> str:
    """
        get string value from parameter
    """
    if key not in advanced_parameters.keys():
        return None
    else:
        return str(advanced_parameters[key])


class Node:
    """
    A class that build triton-model-package to DAG graph.
    """

    def __init__(self, name: str, version_path: str, pbtxt: ModelConfig):
        """
            初始化Node类。
        
        Args:
            name (str): 节点名称。
            version_path (str): digital version path。
            pbtxt (ModelConfig): 模型配置信息。
        
        Returns:
            None.
        
        Raises:
            None.
        """
        self.name = name  # 节点名称
        self.version_path = version_path  # digital version path
        self.in_pin_names = []  # 输入pin名称
        self.out_pin_names = []  # 输出pin名称
        self.in_pin_outer_names = {}  # 输入pin外部名称 inner -> outer
        self.out_pin_outer_names = {}  # 输出pin外部名称 inner -> outer
        self.in_connects = {}  # 输入连接 node->{this_node_in_pin_inner: out_node_out_pin_inner}
        self.out_connects = {}  # 输出连接 node->{this_node_out_pin_inner: out_node_in_pin_inner}
        self.dags = []  # 此节点的内置子dag图，比如ensemble/bls 2-d array
        self.step_models = []  # step
        self.sub_models = []  # bls
        self.python_bls = None
        self.pbtxt = pbtxt
        self.op_resize_output_map = None

    # out_node -> [in_pins]
    def get_out_node_in_pins(self, out_pins: list):
        """
            get in pins of output node
        """
        out_node_in_pins = {}
        for node, pin_pairs in self.out_connects.items():
            for out_pin_inner, out_pin_outer in pin_pairs.items():
                if out_pin_inner in out_pins:
                    if node in out_node_in_pins:
                        out_node_in_pins[node].append(out_pin_outer)
                    else:
                        out_node_in_pins[node] = [out_pin_outer]
        return out_node_in_pins

    def print(self):
        """
            debug use
        """
        bcelogger.info('-----------------------++++++++++++++++++++++++++++------------------------------')
        bcelogger.info('name: {}'.format(self.name))
        bcelogger.info('in_pin_names: {}'.format(self.in_pin_names))
        bcelogger.info('out_pin_names: {}'.format(self.out_pin_names))
        bcelogger.info('in_connects: {}'.format(self.in_connects))
        bcelogger.info('out_connects: {}'.format(self.out_connects))
        bcelogger.info('dags: {}'.format(self.dags))
        bcelogger.info('step_models: {}'.format(self.step_models))
        bcelogger.info('sub_models: {}'.format(self.sub_models))
        bcelogger.info('op_resize_output_map: {}'.format(self.op_resize_output_map))


class PkgDAGBuilder:
    """
    A class that build triton-model-package to DAG graph.
    """

    _default_config_dict: Dict[str, Any] = {}

    def __init__(self, model_repo: str, ensemble_name: str, ensemble_version: str, sub_models: dict):
        """
        build dag
        """
        # 1. build ensemble node
        bcelogger.info('build ensemble node: {}'.format(ensemble_name))
        self.ensemble_node = self._build_node(os.path.join(model_repo, ensemble_name, ensemble_version, PBTXT_NAME),
                                              ensemble_name)
        self.nodes = {self.ensemble_node.name: self.ensemble_node}

        # 2. build other nodes
        for model, version in sub_models.items():
            bcelogger.info('build model node: {}'.format(model))
            self.nodes[model] = self._build_node(os.path.join(model_repo, model, version, PBTXT_NAME), model)

        if len(self.ensemble_node.step_models) < len(sub_models):
            bcelogger.info('need model num: {} got: {}'.format(len(sub_models), len(self.ensemble_node.step_models)))
            self._build_python_bls()

        # 3. build connects
        self._build_connects()
        self.print()

    def modify_connect_model(self, model_name: str, advanced_parameters: dict):
        """
        modify connected nodes
        """
        modify_node_names = {}
        bcelogger.info('advanced_parameters: {}'.format(advanced_parameters))
        # 1. find connected nodes
        if model_name not in self.nodes:
            bcelogger.error('modify model info. do NOT find model: {}'.format(model_name))
            raise ValueError('modify model info. do NOT find model: {}'.format(model_name))

        node = self.nodes[model_name]
        if node is None:
            bcelogger.error('[modify model shape] do NOT found {}'.format(model_name))
            raise ValueError('[modify model shape] do NOT found {}'.format(model_name))

        # 2. modify model input shape
        width = get_int_val(advanced_parameters, ADV_PARAM_WIDTH)
        height = get_int_val(advanced_parameters, ADV_PARAM_HEIGHT)

        batch_size = get_int_val(advanced_parameters, ADV_PARAM_BATCH_SIZE)

        if width is not None and height is not None and batch_size is not None:
            for node_name, in_pairs in node.in_connects.items():
                self._set_preproc_node(node_name, in_pairs.values(), width, height, batch_size)
                modify_node_names[node_name] = node_name

        model_type = get_string_val(advanced_parameters, ADV_PARAM_MODEL_TYPE)
        # 3.1 modify model output shape (ppyoloe only)
        if 'ppyoloe' in model_type:
            max_bbox_count = get_int_val(advanced_parameters, ADV_PARAM_MAX_BBOX_COUNT)
            output_pin_names = ['det_boxes', 'det_scores', 'det_classes']
            # modify model connectes node input shape (ppyoloe only)
            out_node_in_pins = node.get_out_node_in_pins(output_pin_names)
            for out_node_name, in_pins in out_node_in_pins.items():
                out_node = self.nodes[out_node_name]
                out_node.pbtxt.modify_input_dim_value(in_pins, max_bbox_count)
                out_node.pbtxt.write_config_to_file(os.path.join(out_node.version_path, PBTXT_NAME))
                modify_node_names[out_node_name] = out_node_name

        step_models = set()
        sub_models = set()
        for _, node in self.nodes.items():
            for step_model in node.step_models:
                step_models.add((step_model[0]))
            for sub_model in node.sub_models:
                sub_models.add((sub_model[0]))
        bcelogger.info('all step models: {}'.format(step_models))
        bcelogger.info('all sub models: {}'.format(sub_models))

        modify_step_models = {}
        modify_sub_models = {}
        for name, _ in modify_node_names.items():
            if name in step_models:
                modify_step_models[name] = ""
            if name in sub_models:
                modify_sub_models[name] = ""

        return modify_step_models, modify_sub_models

    def modify_ensemble(self, model_name_pairs: dict):
        """
        modify ensemble node
        """
        need_clear_dag = False
        bcelogger.info('modify model name pair. {}'.format(model_name_pairs))

        for name, node in self.nodes.items():
            if node.pbtxt.modify_model_name(model_name_pairs):
                node.pbtxt.write_config_to_file(os.path.join(node.version_path, PBTXT_NAME))
                need_clear_dag = True

            if node.python_bls is not None:
                node.python_bls.replace_model_names(model_name_pairs, node.version_path)

        if need_clear_dag:
            self.nodes = {}
            self.ensemble_node = None

    def print(self):
        """
            debug use only
        """
        for n in self.nodes:
            self.nodes[n].print()

    def _set_preproc_node(self, node_name: str, output_names: list, width: int, height: int, batch_size: int):
        """
            set preprocess node width/height output
        """
        node = self.nodes[node_name]
        if node.pbtxt.get_field(KEY_BACKEND) in [BACKEND_NAME_OP, BACKEND_NAME_PYTHON]:
            node.pbtxt.set_preproc_width_height(output_names, width, height)
            if node.pbtxt.get_field(KEY_MAX_BATCH_SIZE) > batch_size:
                node.pbtxt.set_field(KEY_MAX_BATCH_SIZE, batch_size)
                node.pbtxt.modify_dynamic_batching(batch_size)
        node.pbtxt.write_config_to_file(os.path.join(node.version_path, PBTXT_NAME))

    def _build_python_bls(self):
        """
            get python bls model name, etc
        """
        for n in self.ensemble_node.step_models:
            python_bls = PythonBLSProcessor(self.nodes[n[0]].version_path)
            if len(python_bls.model_name_lines) > 0:
                self.nodes[n[0]].python_bls = python_bls

    def _build_node(self, pbtxt_path: str, model_name: str):
        """
            build node of dag
        """
        # 1. build common config
        pbtxt = ModelConfig._create_from_file(pbtxt_path)
        node = Node(pbtxt.get_field(KEY_NAME), os.path.dirname(pbtxt_path), pbtxt)
        if len(node.name) <= 0:
            node.name = model_name
        node.op_resize_output_map = pbtxt.get_op_resize_output_map()
        node.in_pin_names = pbtxt.get_input_names()
        node.out_pin_names = pbtxt.get_ouput_names()

        # 2. build connects
        if pbtxt.is_ensemble():
            node.step_models = pbtxt.get_ensemble_composing_step()
        if pbtxt.get_field(KEY_BACKEND) == BACKEND_NAME_BLS:
            node.sub_models = pbtxt.get_bls_optmization()

        return node

    def _find_model_name_by_pin_out(self, pin_out_name, name_version_in_out, map_idx):
        """
            get model name and pin in from model-version-in-out
        """
        out_node_name_pin_inners = []
        for n in name_version_in_out:
            for k, v in n[map_idx].items():
                if v == pin_out_name:
                    out_node_name_pin_inners.append([n[0], k])

        return out_node_name_pin_inners

    def _build_in_out_connects(self, name_version_in_out: list, ensemble_node: Node):
        """
            build node in/out connects
        """
        for n in name_version_in_out:
            model_name, model_version, in_map, out_map = n
            node = self.nodes[model_name]

            # in connects
            for inner_pin, outer_pin in in_map.items():
                out_node_name_pin_inners = self._find_model_name_by_pin_out(outer_pin, name_version_in_out, 3)
                if len(out_node_name_pin_inners) <= 0:
                    # find in ensemble node
                    if outer_pin in ensemble_node.in_pin_names:
                        out_node_name_pin_inners.append([ensemble_node.name, outer_pin])

                if len(out_node_name_pin_inners) <= 0:
                    bcelogger.error('not found in connects. model: {} out: {}'.format(model_name, outer_pin))
                    continue

                for out_node_name, out_node_pin_inner in out_node_name_pin_inners:
                    if out_node_name in node.in_connects:
                        node.in_connects[out_node_name][inner_pin] = out_node_pin_inner
                    else:
                        node.in_connects[out_node_name] = {inner_pin: out_node_pin_inner}

            # out connects
            for inner_pin, outer_pin in out_map.items():
                out_node_name_pin_inners = self._find_model_name_by_pin_out(outer_pin, name_version_in_out, 2)

                if len(out_node_name_pin_inners) <= 0:
                    # find in ensemble node
                    if outer_pin in ensemble_node.out_pin_names:
                        out_node_name_pin_inners.append([ensemble_node.name, outer_pin])
                if len(out_node_name_pin_inners) <= 0:
                    bcelogger.error('not found out connects. model: {} out: {}'.format(model_name, outer_pin))
                    continue
                for out_node_name, out_node_pin_inner in out_node_name_pin_inners:
                    if out_node_name in node.out_connects:
                        node.out_connects[out_node_name][inner_pin] = out_node_pin_inner
                    else:
                        node.out_connects[out_node_name] = {inner_pin: out_node_pin_inner}

    def _build_connects(self):
        """
        build connects of nodes by ensemble/bls
        """
        # 1. find ensembles/bls
        for name, node in self.nodes.items():
            name_version_in_out = []
            if len(node.step_models) > 0:
                name_version_in_out = node.step_models
            if len(node.sub_models) > 0:
                for s in node.sub_models:
                    name_version_in_out.append(s[0: 4])

            if len(name_version_in_out) > 0:
                # 2. ensemble/bls retrive node & connect
                self._build_in_out_connects(name_version_in_out, node)


if __name__ == "__main__":
    pkg_idx = 0
    if pkg_idx == 0:
        pkg_path = '/ssd2/wgf/pkg/20240328/human_attribute_851_v2_5_20_1_240313'
        ensemble_name = 'ensemble'
        model_name_versions = {
            'classifier': '1',
            'crop': '1',
            'crop_postproc': '1',
            'det_postproc': '1',
            'det_preproc': '1',
            'detect': '1',
            'detect_attr': '1',
            ensemble_name: '1',
            'human_classifier': '1',
            'postprocess': '1'
        }
    elif pkg_idx == 1:
        pkg_path = '/ssd2/wgf/pkg/20240328/human_attribute_firesmoke_t4_v3.2.1'
        ensemble_name = 'human-fire-ensemble'
        model_name_versions = {
            'human-fire-attr_clas_model': '1',
            'human-fire-attr_layout': '1',
            'human-fire-det_preproc': '1',
            'human-fire-fire_class_model': '1',
            'human-fire-postprocess': '1',
            'human-fire-attr_det_model': '1',
            'human-fire-attr_preproc': '1',
            'human-fire-detect': '1',
            'human-fire-fire_class_preproc': '1',
            'human-fire-attr_human_clas_model': '1',
            'human-fire-bls': '1',
            ensemble_name: '1',
            'human-fire-fire_classifier': '1'
        }
    elif pkg_idx == 2:
        pkg_path = '/ssd2/wgf/pkg/20240318/universal-single-attr-cls'
        ensemble_name = 'single-attr-cls-ensemble'
        model_name_versions = {
            ensemble_name: '1',
            'single-attr-cls-model': '1',
            'single-attr-cls-postprocess': '1',
            'single-attr-cls-preprocess': '1'
        }
    elif pkg_idx == 3:
        pkg_path = '/ssd2/wgf/pkg/20240103/universal_ppyoloeplus'
        ensemble_name = 'ppyoloeplus-ensemble'
        model_name_versions = {
            ensemble_name: '1',
            'ppyoloeplus-model': '1',
            'ppyoloeplus-preprocess': '1',
            'ppyoloeplus-postprocess': '1'
        }
    elif pkg_idx == 4:
        pkg_path = '/ssd2/wgf/pkg/20240328/single_model'
        ensemble_name = ''
        model_name_versions = {
            'detect': '1',
            ensemble_name: ''
        }
    builder = PkgDAGBuilder(pkg_path, ensemble_name, model_name_versions, {})

    advanced_parameters = {
        ADV_PARAM_WIDTH: 1000,
        ADV_PARAM_HEIGHT: 500,
        ADV_PARAM_CHANNEL: 3,
        ADV_PARAM_BATCH_SIZE: 50,
        ADV_PARAM_MAX_BBOX_COUNT: 100,
        ADV_PARAM_MODEL_TYPE: 'ppyoloe',
        ADV_PARAM_MODEL_NAME_PAIR: {
            'ppyoloeplus-preprocess': ['abc-preprocess', 6],
            'ppyoloeplus-model': ['abc-model', 6],
            'ppyoloeplus-postprocess': ['abc-postprocess', 6],
            'classifier': ['classifier11', 6],
            'detect': ['detect2', 6]
        }
    }
    builder.modify_model_info('detect', advanced_parameters)
