#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/8/9
# @Author  : yanxiaodong
# @File    : bls_processor.py
"""
import os
import re
from typing import Dict
from collections import defaultdict

import bcelogger
from windmillmodelv1.client.model_api_model import ModelName

from .model_config import ModelConfig


class GaeaBLSParser(object):
    """
    BLS processor.
    """

    def __init__(self,
                 client,
                 workspace_id: str,
                 model_store_name: str,
                 input_uri: str = "/home/windmill/tmp/model"):
        self.windmill_client = client
        self.workspace_id = workspace_id
        self.model_store_name = model_store_name
        self.input_uri = input_uri

    def from_optimization(self, model_name: str, model_uri: str, ensemble_steps: Dict, sub_models: Dict):
        """
        Get the BLS processor from the optimization.
        """
        model_config = ModelConfig.create_from_file(
            model_config_filepath=os.path.join(model_uri, "config.pbtxt"))
        if not model_config.is_bls():
            bcelogger.info(f"Model name {model_name} is not BLS")
            return {}

        optimization = model_config.as_dict().get("optimization", {})
        if len(optimization.get("executionAccelerators", {})) == 0:
            bcelogger.info(f"Model name {model_name} is not BLS")
            return {}

        if len(optimization["optimization"].get("gpuExecutionAccelerator", [])) == 0:
            bcelogger.info(f"Model name {model_name} is not BLS")
            return {}

        bcelogger.info(f"BLS is {model_name}, optimization is {optimization}")
        bcelogger.info(f"Current step is {ensemble_steps}")
        bls = ensemble_steps.pop(model_name)

        for execution_accelerator in optimization["executionAccelerators"]["gpuExecutionAccelerator"]:
            if "model_name" not in execution_accelerator["parameters"]:
                continue

            name = execution_accelerator["parameters"]["model_name"]
            sub_models[name] = sub_models.get(name, "latest")
            bcelogger.info(f"Model name {name} version {sub_models[name]}")

            input_map = {}
            output_map = {}
            for key, value in execution_accelerator["parameters"].items():
                if key.startswith('IN'):
                    input_map[value.split(":")[0]] = bls["inputMap"][value.split(":")[1]]
                if key.startswith('OUT'):
                    output_map[value.split(":")[0]] = bls["outputMap"][value.split(":")[1]]
                if key.startswith("filter_map"):
                    input_map[value.split(":")[0]] = bls["inputMap"][value.split(":")[0]]
                    output_map[value.split(":")[1]] = bls["outputMap"][value.split(":")[1]]
            bcelogger.info(f"Model name {name}, input map is {input_map}")
            bcelogger.info(f"Model name {name}, output map is {output_map}")

            ensemble_steps.update(self._parse_bls_models(name,
                                                         sub_models[name],
                                                         input_map,
                                                         output_map,
                                                         sub_models))

    def from_python_script(self, model_name: str, model_uri: str, ensemble_steps: Dict, sub_models: Dict):
        """
        Get the BLS processor from the python script.
        """
        script_filepath = os.path.join(model_uri, "model.py")
        if not os.path.exists(script_filepath):
            bcelogger.info(f"Model name {model_name} python script is not exist {script_filepath}")
            return {}

        bcelogger.info(f"Python script is {script_filepath}")
        data_raw = open(script_filepath, "r").readlines()

        pattern = r'pb_utils\.InferenceRequest\(\s*([^\)]*)\s*\)'
        matches = re.findall(pattern, str(data_raw), re.DOTALL)

        if len(matches) == 0:
            bcelogger.info(f"Do not find model in {script_filepath}")
            return {}

        bls = ensemble_steps.pop(model_name)
        for match in matches:
            bcelogger.info(f"Match model is {match}")
            if match == "":
                continue

            name = re.search(r'model_name="([^"]+)"', match).group(1)
            sub_models[name] = sub_models.get(name, "latest")
            bcelogger.info(f"Model name {name} version {sub_models[name]}")

            ensemble_steps.update(self._parse_bls_models(name,
                                                         sub_models[name],
                                                         bls["inputMap"],
                                                         bls["outputMap"],
                                                         sub_models))

    def __call__(self, model_name: str, model_uri: str, ensemble_steps: Dict, sub_models: Dict):
        """
        Get bls
        """
        self.from_optimization(model_name=model_name,
                               model_uri=model_uri,
                               ensemble_steps=ensemble_steps,
                               sub_models=sub_models)
        self.from_python_script(model_name=model_name,
                                model_uri=model_uri,
                                ensemble_steps=ensemble_steps,
                                sub_models=sub_models)

    def _parse_bls_models(self,
                          model_name: str,
                          model_version: str,
                          input_map: Dict,
                          output_map: Dict,
                          sub_models: Dict):
        """
        Parse the bls models.
        """
        object_name = ModelName(workspace_id=self.workspace_id,
                                model_store_name=self.model_store_name,
                                local_name=model_name).get_name()
        model_output_uri = os.path.join(self.input_uri, model_name)
        self.windmill_client.download_artifact(object_name=object_name,
                                               version=model_version,
                                               output_uri=model_output_uri)

        model_config = ModelConfig.create_from_file(
            model_config_filepath=os.path.join(model_output_uri, "config.pbtxt"))

        steps = defaultdict(dict)
        if not model_config.is_ensemble():
            steps[model_name] = {"modelName": model_name,
                                 "modelVersion": model_version,
                                 "inputMap": input_map,
                                 "outputMap": output_map}
            return steps

        for name, step in model_config.get_ensemble_steps().items():
            bcelogger.info(f"Parsing step {name} is {step}")
            sub_models[name] = sub_models.get(name, "latest")
            bcelogger.info(f"Model name {name} version {sub_models[name]}")

            for key, value in step["inputMap"].items():
                bcelogger.info(f"Model {name} inputs for {key}:{value} and input map {input_map}")
                if value in input_map:
                    step["inputMap"][key] = input_map[value]

            for key, value in step["outputMap"].items():
                bcelogger.info(f"Model {name} outputs for {key}:{value} and output map {output_map}")
                if value in output_map:
                    step["outputMap"][key] = output_map[value]

            steps[name] = step

        return steps
