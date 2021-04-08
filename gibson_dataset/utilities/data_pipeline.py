import queue
from typing import Callable

import numpy as np
import gibson_dataset.utilities.engine_selector as eg


class DataPipeline:
    """
    This class constructs an elaboration pipeline to elaborate a single data.
    A pipeline is composed by a series of consecutive operations performed to the same data.
    A pipeline can be executed in CPU or GPU (using CuPy)
    :
    """

    def __init__(self, data: np.array, use_gpu: bool, end_function: Callable[[np.array], np.array] = lambda data: data):
        """
        Creates a new pipeline
        :param data: the data to be modified
        :param use_gpu: indicates of the pipeline must be executed in gpu
        :param end_function: a function which can be used to automatically save the data outside the pipeline
        """
        self._data = data
        self._use_gpu = use_gpu
        self._end_function = end_function
        self._operations = queue.Queue()

        self._xp = eg.get_engine(eg.NUMPY if not use_gpu else eg.CUPY)

        # IF the pipeline is executed in gpu, transfer data to device mandatory
        if use_gpu:
            self._cuda_stream = self._xp.cuda.Stream(non_blocking=True)
            self._transfer_data_to_device()

    def _transfer_data_to_device(self) -> 'DataPipeline':
        """
        Adds to the pipeline's operations the data migration to GPU
        :return: return the pipeline
        :rtype DataPipeline
        """
        self._operations.put(lambda data: self._xp.asarray(data))

        return self

    def _get_data_from_device(self) -> 'DataPipeline':
        """
        Obtains the data from GPU
        :return: return the pipeline
        :rtype DataPipeline
        """
        self._operations.put(lambda data: self._xp.asnumpy(data, stream=self._cuda_stream))

        return self

    def run(self) -> 'DataPipeline':
        """
        Runs the pipeline returning the modified data.
        Note that if the pipeline uses GPU, this is an ASYNC operation.
        :return: the modified data
        :rtype np.array
        """
        if self._use_gpu:
            self._get_data_from_device()

        ret = self._data

        if self._use_gpu:
            self._cuda_stream.use()
        for operation in self._operations.queue:
            ret = operation(ret)

        self._data = ret

        return self

    def obtain_data(self) -> np.array:
        """
        Returns the data after the pipeline execution finishes and call the end-function specified in the constructor.
        This a SYNC operation, so if the pipeline is running using GPU,
        the current thread is blocked until all operations in the pipeline are completed.
        :return: np.array
        :rtype np.array
        """
        if self._use_gpu:
            self._cuda_stream.synchronize()

        return self._end_function(self._data)

    def convert_bgr_to_rgb(self) -> 'DataPipeline':
        """
        Adds to the pipeline's operations the conversion from BGR to RGB
        :return: the pipeline
        :rtype DataPipeline
        """
        self._operations.put(lambda data: data[..., [2, 1, 0]])

        return self

    def convert_rgb_to_bgr(self) -> 'DataPipeline':
        """
        Adds to the pipeline's operations the conversion from RGB to BGR
        :return: the pipeline
        :rtype DataPipeline
        """
        self._operations.put(lambda data: data[..., ::-1])

        return self

    def around(self, decimals: int = 0) -> 'DataPipeline':
        """
        Round an array of float to the given number of decimals
        :param decimals: the number of decimal places to round
        :type decimals: int
        :return: the pipeline
        :rtype DataPipeline
        """
        self._operations.put(lambda data: self._xp.around(data, decimals=decimals))

        return self
