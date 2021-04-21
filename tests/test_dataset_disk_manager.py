import os

import numpy as np
from generic_dataset.data_pipeline import DataPipeline
from generic_dataset.dataset_disk_manager import DatasetDiskManager
from generic_dataset.sample_generator import SampleGenerator

pipeline_field_1_2 = DataPipeline().add_operation(lambda data, engine: (engine.array([1 for i in range(10000)]), engine))
GeneratedSample = SampleGenerator(name='GeneratedSample').add_field(field_name='field_1', field_type=np.ndarray, add_to_dataset=True) \
    .add_field(field_name='field_2', field_type=np.ndarray, add_to_dataset=True) \
    .add_field(field_name='field_3', field_type=np.ndarray, add_to_dataset=False) \
    .add_custom_pipeline(method_name='pipeline_field_1_2', elaborated_field='field_1', final_field='field_2', pipeline=pipeline_field_1_2) \
    .generate_sample_class()


def test_constructor():
    path = os.path.join(os.path.dirname(__file__), 'dataset_folder')
    DatasetDiskManager(dataset_path=path, folder_name='folder', sample=GeneratedSample(is_positive=False))
    DatasetDiskManager(dataset_path=path, folder_name='folder1', sample=GeneratedSample(is_positive=False))
    DatasetDiskManager(dataset_path=path, folder_name='folder1', sample=GeneratedSample(is_positive=False))