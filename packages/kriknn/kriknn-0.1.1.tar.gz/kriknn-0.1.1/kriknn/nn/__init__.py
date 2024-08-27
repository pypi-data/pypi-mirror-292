import numpy as np
from kriknn.engine.tensor import Tensor


class Linear:
    def __init__(self, features_in, features_out):
        self.weight = Tensor(np.random.uniform(-1 / np.sqrt(features_in),
                             1 / np.sqrt(features_in), (features_in, features_out)))
        self.bias = Tensor(np.random.uniform(-1 / np.sqrt(features_in),
                           1 / np.sqrt(features_in), (features_out,)))

    def __call__(self, x: Tensor) -> Tensor:
        return x @ self.weight + self.bias
