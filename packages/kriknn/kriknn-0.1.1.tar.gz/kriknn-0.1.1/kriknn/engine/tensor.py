import numpy as np


class Tensor:
    def __init__(self, data, dtype=np.float32):
        if isinstance(data, list):
            self.data = np.array(data, dtype=dtype)
        elif isinstance(data, np.ndarray):
            self.data = data
        elif isinstance(data, (int, float)):
            self.data = np.array(data, dtype=dtype)
        else:
            raise TypeError(
                "Data must be a list, a numpy array, or a scalar (int/float).")
        self.dtype = dtype
        self.shape = self.data.shape

    def __repr__(self):
        return f"Tensor(shape={self.shape}, dtype={self.dtype}, data={self.data})"

    def __matmul__(self, other):
        if not isinstance(other, Tensor):
            raise TypeError(
                f"Unsupported operand type(s) for @: 'Tensor' and '{type(other).__name__}'")
        return Tensor(np.matmul(self.data, other.data))

    def __add__(self, other):
        if not isinstance(other, Tensor):
            raise TypeError(
                f"Unsupported operand type(s) for +: 'Tensor' and '{type(other).__name__}'")
        return Tensor(self.data + other.data)

    def get_data(self):
        return self.data

    @staticmethod
    def zeros(shape, dtype=np.float32):
        return Tensor(np.zeros(shape, dtype=dtype))

    @staticmethod
    def ones(shape, dtype=np.float32):
        return Tensor(np.ones(shape, dtype=dtype))

    @staticmethod
    def uniform(shape, low=0.0, high=1.0, dtype=np.float32):
        return Tensor(np.random.uniform(low, high, size=shape).astype(dtype))

    def add(self, other):
        if isinstance(other, Tensor):
            return Tensor(self.data + other.data, dtype=self.dtype)
        else:
            raise TypeError("Operand must be a Tensor.")

    def mul(self, other):
        if isinstance(other, Tensor):
            return Tensor(self.data * other.data, dtype=self.dtype)
        else:
            raise TypeError("Operand must be a Tensor.")

    def dot(self, other):
        if isinstance(other, Tensor):
            return Tensor(np.dot(self.data, other.data), dtype=self.dtype)
        else:
            raise TypeError("Operand must be a Tensor.")

    def transpose(self):
        return Tensor(self.data.T, dtype=self.dtype)

    def linear(self, weight, bias=None):
        if not isinstance(weight, Tensor):
            raise TypeError("Weight must be a Tensor.")
        if bias is not None and not isinstance(bias, Tensor):
            raise TypeError("Bias must be a Tensor or None.")

        if bias is not None:
            return self.dot(weight).add(bias)
        else:
            return self.dot(weight)
