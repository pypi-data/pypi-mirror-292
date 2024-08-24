# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
解析python BLS代码，找到调用的推理模型名称（最大程度兼容模型包）
- 仅支持调用的推理模型名称修改
- 不支持模型预处理的width/height等信息修改
Authors: wanggaofei(wanggaofei03@baidu.com)
Date:    2023-03-29
"""
import os
import sys
import bcelogger
from typing import Any, Dict, List, Optional

MODEL_PY_NAME = 'model.py'
MODEL_INFER_FUNCTION_NAME = 'pb_utils.InferenceRequest'
PARENTHESIS_LEFT = '('
PARENTHESIS_RIGHT = ')'
PARAMETER_MODEL_NAME = 'model_name'

class PythonBLSProcessor:
    """
    A class that parse python bls & modify sub_infer_model_name
        - 1. only modify sub_infer_model_name
        - 2. do NOT support modify sub_infer_model preprocess width/height
    """

    _default_config_dict: Dict[str, Any] = {}

    def __init__(self, version_path: str):
        """
            model.py path
        """
        self.py_name = os.path.join(version_path, MODEL_PY_NAME)
        self.lines = self._read_lines(self.py_name)
        self.model_name_lines = self.search_all_infer_model_names()
    
    def _read_lines(self, name: str) -> List[str]:
        """
            read txt file lines
        """
        if os.path.exists(name):
            return open(name).readlines()
        else:
            return []

    def _skip_comment_lines(self, begin_line):
        """
            skip comment codes
        """
        comments = ["'''", '"""']
        idx = 0
        while begin_line < len(self.lines):
            comment_flag = None
            idx += 1
            for c in comments:
                if self.lines[begin_line].strip().startswith(c):
                    comment_flag = c
                    begin_line += 1
                    break
            if comment_flag is not None:
                comment_right = len(self.lines)
                for i in range(begin_line, len(self.lines)):
                    if self.lines[i].strip().startswith(comment_flag):
                        comment_right = i
                        break
                begin_line = comment_right + 1
            else:
                return begin_line
        return begin_line

    def _find_str_line(self, begin_line: int, str_val: str) -> int:
        """
            find string value from xxx line
        """
        while begin_line < len(self.lines):
            # skip comment line
            begin_line = self._skip_comment_lines(begin_line)
            
            if begin_line < len(self.lines) and str_val in self.lines[begin_line] \
                and not self.lines[begin_line].strip().startswith('#'):
                return begin_line
            begin_line += 1
        
        return begin_line # do NOT find

    def _get_parameter_value(self, line: str, parameter: str):
        """
            get function parameter
        """
        bcelogger.info('LINE: {}'.format(line))
        line_str = line.strip()
        pos = line_str.find(parameter)
        sub_line = line_str[pos: ]
        equal_pos = sub_line.find('=')
        sub_line = sub_line[equal_pos + 1: ].strip()
        if len(sub_line) <= 0 or sub_line[0] not in ['"', "'"]:
            raise ValueError('do NOT support python-bls: {}'.format(sub_line))
        sign = sub_line[0]
        sub_line = sub_line[1: ]
        end_pos = sub_line.find(sign)
        return sub_line[0: end_pos]
        
    def _find_model_name(self, begin_line: int) -> Optional[str]:
        """
            find infer model name
        """
        function_pos = self._find_str_line(begin_line, MODEL_INFER_FUNCTION_NAME)
        if function_pos >= len(self.lines):
            return None, function_pos

        parenthesis_left = self._find_str_line(function_pos, PARENTHESIS_LEFT)
        if parenthesis_left >= len(self.lines):
            return None, parenthesis_left

        parenthesis_right = self._find_str_line(function_pos, PARENTHESIS_RIGHT)
        if parenthesis_right >= len(self.lines):
            return None, parenthesis_right

        for i in range(parenthesis_left, parenthesis_right + 1):
            if PARAMETER_MODEL_NAME in self.lines[i]:
                model_name = self._get_parameter_value(self.lines[i], PARAMETER_MODEL_NAME)
                bcelogger.info('model_name: {}'.format(model_name))
                if model_name is None or len(model_name) <= 0:
                    raise ValueError('do NOT support python-bls: {}'.format(self.lines[i]))
                return model_name, i
        return None, parenthesis_right + 1

    def search_all_infer_model_names(self):
        """
            search all infer models
        """
        model_name_lines = {}
        begin_line = 0
        while True:
            model_name, line = self._find_model_name(begin_line)
            begin_line = line + 1
            if begin_line >= len(self.lines):
                break
            if model_name is None:
                continue

            model_name_lines[model_name] = line
            
        if len(model_name_lines) <= 0:
                bcelogger.error('do NOT find {} in {}'.format(MODEL_INFER_FUNCTION_NAME, self.py_name))
        bcelogger.info('model_name_lines: {}'.format(model_name_lines))
        return model_name_lines
    
    def replace_model_names(self, model_name_pair: dict, version_path: str):
        """
            replace all model names by pair
        """
        need_save_py = False
        for old_name, new_name_version in model_name_pair.items():
            if old_name not in self.model_name_lines:
                bcelogger.warning('do NOT find {} in {}'.format(old_name, self.model_name_lines))
            else:
                self.lines[self.model_name_lines[old_name]] = \
                    self.lines[self.model_name_lines[old_name]].replace(old_name, new_name_version[0])
                bcelogger.info('replace model name: {}'.format(self.lines[self.model_name_lines[old_name]]))
                need_save_py = True
        if need_save_py:
            self._write_file(version_path, MODEL_PY_NAME)
            bcelogger.info('save {} to {}'.format(MODEL_PY_NAME, version_path))
        return need_save_py
        
    def _write_file(self, output_dir: str, file_name: str=MODEL_PY_NAME):
        """
        Write to model.py
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(os.path.join(output_dir, file_name), "w") as f:
            for line in self.lines:
                f.write(line)

if __name__ == '__main__':
    model_version_path = '/ssd2/wgf/pkg/20240328/human_attribute_851_v2_5_20_1_240313/crop/1'
    python_bls = PythonBLSProcessor(model_version_path)
    model_name_pair = {
        'classifier1': ['classifier2', 6],
        'detect_attr': ['detect_attr2', 6],
        'human_classifier': ['human_classifier2', 6]
    }
    python_bls.replace_model_names(model_name_pair, '.')