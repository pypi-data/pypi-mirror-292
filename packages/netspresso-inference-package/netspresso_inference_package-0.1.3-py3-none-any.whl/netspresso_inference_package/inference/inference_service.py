import os
from pathlib import Path
from typing import Dict, Any

import numpy as np
from loguru import logger

from .tflite_inference import TFLITE
from .onnx_inference import ONNX
from .data_loader import NumpyDataLoader
from ..utils import make_temp_dir, compress_files, delete_parent_directory
from ..exceptions import NotSupportedFramework


class InferenceService:
    def __init__(self, model_file_path:str, dataset_file_path:str, num_threads:int=1):
        self.model_file_path = model_file_path
        self.dataset_file_path = dataset_file_path
        self.model_obj, self.inputs, self.outputs = self.set_model_obj(model_file_path, num_threads)
        self.data_loader = NumpyDataLoader(dataset_file_path, self.inputs)
        self.data_loader.load_datasets(dataset_file_path, self.inputs)
        self.result_save_path = make_temp_dir()

    def set_model_obj(self, model_file_path:str, num_threads:int):
        suffix = Path(model_file_path).suffix
        if suffix == ".tflite":
            model_obj = TFLITE(model_file_path, num_threads)
        elif suffix == ".onnx":
            model_obj = ONNX(model_file_path, num_threads)
        else:
            raise NotSupportedFramework()
        # TODO: check framework by model file inspector
        # model_info = validate_model_file(model_file_path)
        # if model_info[Enums.FRAMEWORK] == Enums.TFLITE:
        #     model_obj = TFLITE(model_file_path, kwargs["num_threads"])
        # elif model_info[Enums.FRAMEWORK] == Enums.ONNX:
        #     model_obj = ONNX(model_file_path)
        
        if len(model_obj.inputs) > 1:
            logger.info(f'{self.model_file_path} has {len(model_obj.inputs)} nodes for input layer')
        if len(model_obj.outputs) > 1:
            logger.info(f'{self.model_file_path} has {len(model_obj.outputs)} nodes for output layer')
        return model_obj, model_obj.inputs, model_obj.outputs

    def inference(self):
        try:
            return self.model_obj.inference(self.data_loader.npy)
        except Exception as e: # TODO make a exception
            raise e

    def postprocess(self, inference_results:Dict[Any, np.ndarray]):
        # save npy file for each layers result
        files_path = []
        result_file_path = os.path.join(self.result_save_path, "archive.zip")
        for k, v in inference_results.items():
            npy_file_path = os.path.join(self.result_save_path, f"{k}.npy")
            np.save(npy_file_path, inference_results[k])
            files_path.append(npy_file_path)
        # zip npy files
        compress_files(files_path, result_file_path)
        self.result_file_path = result_file_path
    
    def run(self):
        inference_results = self.inference()
        logger.info(f"Inference success: {self.model_file_path}")
        self.postprocess(inference_results)


if __name__ == "__main__":

    inf_service = InferenceService(
        model_file_path="/app/tests/people_detection.onnx",
        dataset_file_path="/app/tests/dataset_for_onnx.npy"
        )
    inf_service.run()