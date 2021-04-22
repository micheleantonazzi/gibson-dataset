import os
import shutil

import numpy as np
import pytest

from generic_dataset.data_pipeline import DataPipeline
from generic_dataset.dataset_disk_manager import DatasetDiskManager
from generic_dataset.sample_generator import SampleGenerator
import generic_dataset.utilities.save_load_methods as slm


pipeline_field_1_2 = DataPipeline().add_operation(lambda data, engine: (engine.array([1 for i in range(10000)]), engine))
GeneratedSample = SampleGenerator(name='GeneratedSample') \
    .add_dataset_field(field_name='field_1', field_type=np.ndarray, save_function=slm.save_compressed_numpy_array, load_function=slm.save_compressed_numpy_array) \
    .add_dataset_field(field_name='field_2', field_type=np.ndarray, save_function=slm.save_compressed_numpy_array, load_function=slm.save_compressed_numpy_array) \
    .add_field(field_name='field_3', field_type=np.ndarray) \
    .add_custom_pipeline(method_name='pipeline_field_1_2', elaborated_field='field_1', final_field='field_2', pipeline=pipeline_field_1_2) \
    .generate_sample_class()

path = os.path.join(os.path.dirname(__file__), 'dataset_folder')


def test_constructor():
    with pytest.raises(FileNotFoundError):
        DatasetDiskManager(dataset_path='random_path', folder_name='folder', sample=GeneratedSample(is_positive=False))

    DatasetDiskManager(dataset_path=path, folder_name='folder', sample=GeneratedSample(is_positive=False))
    DatasetDiskManager(dataset_path=path, folder_name='folder1', sample=GeneratedSample(is_positive=False))
    DatasetDiskManager(dataset_path=path, folder_name='folder1', sample=GeneratedSample(is_positive=False))


def test_count_samples():
    shutil.rmtree(path, ignore_errors=True)
    dataset = DatasetDiskManager(dataset_path=path, folder_name='folder', sample=GeneratedSample(is_positive=False))

    assert dataset.get_negative_samples_count() == 0
    assert dataset.get_positive_samples_count() == 0


def test_save_fields():
    shutil.rmtree(path, ignore_errors=True)
    dataset = DatasetDiskManager(dataset_path=path, folder_name='folder', sample=GeneratedSample(is_positive=False))

    sample = GeneratedSample(is_positive=False).set_field_1(np.array([11.1 for _ in range(10000)])).set_field_2(np.array([1 for _ in range(10000)]))
    dataset.save_sample(sample, False)

    sample = GeneratedSample(is_positive=True).set_field_1(np.array([11.1 for _ in range(10000)])).set_field_2(np.array([1 for _ in range(10000)]))
    dataset.save_sample(sample, True)

    sample = GeneratedSample(is_positive=False).set_field_1(np.array([11.1 for _ in range(10000)])).set_field_2(np.array([1 for _ in range(10000)]))
    dataset.save_sample(sample, True)

    sample = GeneratedSample(is_positive=True).set_field_1(np.array([11.1 for _ in range(10000)])).set_field_2(np.array([1 for _ in range(10000)]))
    dataset.save_sample(sample, True)

    assert dataset.get_negative_samples_count() == 2
    assert dataset.get_positive_samples_count() == 2
