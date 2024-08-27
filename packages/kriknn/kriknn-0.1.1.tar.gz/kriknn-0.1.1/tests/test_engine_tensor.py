import unittest
import numpy as np
from kriknn.engine.tensor import Tensor

class TestTensor(unittest.TestCase):
    def test_tensor_initialization(self):
        # Test initialization with different data types
        data = [[1.0, 2.0], [3.0, 4.0]]
        tensor = Tensor(data)
        self.assertTrue(np.array_equal(
            tensor.data, np.array(data, dtype=np.float32)))

        # Test initialization with different dtype
        tensor_int = Tensor(data, dtype=np.int32)
        self.assertTrue(np.array_equal(tensor_int.data,
                        np.array(data, dtype=np.int32)))

    def test_tensor_shape(self):
        data = [[1.0, 2.0], [3.0, 4.0]]
        tensor = Tensor(data)
        self.assertEqual(tensor.shape, (2, 2))

    def test_repr(self):
        data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        tensor = Tensor(data)
        expected_repr = f"Tensor(shape={tensor.shape}, dtype={tensor.dtype}, data={tensor.data})"
        self.assertEqual(repr(tensor), expected_repr)

    def test_get_data(self):
        data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        tensor = Tensor(data)
        retrieved_data = tensor.get_data()
        expected_data = np.array(data, dtype=np.float32)
        np.testing.assert_array_equal(retrieved_data, expected_data)

    def test_tensor_matrix_multiplication(self):
        data1 = [[1.0, 2.0], [3.0, 4.0]]
        data2 = [[2.0, 0.0], [1.0, 2.0]]
        tensor1 = Tensor(data1)
        tensor2 = Tensor(data2)

        result = tensor1 @ tensor2
        expected_result = np.array([[4.0, 4.0], [10.0, 8.0]], dtype=np.float32)
        self.assertTrue(np.allclose(result.data, expected_result))

    def test_tensor_addition(self):
        data1 = [[1.0, 2.0], [3.0, 4.0]]
        data2 = [[5.0, 6.0], [7.0, 8.0]]
        tensor1 = Tensor(data1)
        tensor2 = Tensor(data2)

        result = tensor1 + tensor2
        expected_result = np.array(
            [[6.0, 8.0], [10.0, 12.0]], dtype=np.float32)
        self.assertTrue(np.allclose(result.data, expected_result))

    def test_tensor_matrix_multiplication_invalid_type(self):
        tensor1 = Tensor([[1.0, 2.0]])
        with self.assertRaises(TypeError):
            # Invalid type for matrix multiplication
            result = tensor1 @ [[1.0], [2.0]]

    def test_tensor_addition_invalid_type(self):
        tensor1 = Tensor([[1.0, 2.0]])
        with self.assertRaises(TypeError):
            # Invalid type for addition
            result = tensor1 + [[1.0, 2.0]]

    def test_zeros(self):
        tensor = Tensor.zeros((2, 3))
        expected = np.zeros((2, 3), dtype=np.float32)
        np.testing.assert_array_equal(tensor.data, expected)

    def test_ones(self):
        tensor = Tensor.ones((3, 2))
        expected = np.ones((3, 2), dtype=np.float32)
        np.testing.assert_array_equal(tensor.data, expected)

    def test_uniform(self):
        tensor = Tensor.uniform((2, 2), low=0, high=1)
        self.assertEqual(tensor.shape, (2, 2))
        self.assertTrue((tensor.data >= 0).all() and (tensor.data < 1).all())

    def test_add(self):
        tensor1 = Tensor([[1, 2], [3, 4]])
        tensor2 = Tensor([[5, 6], [7, 8]])
        result = tensor1.add(tensor2)
        expected = np.array([[6, 8], [10, 12]], dtype=np.float32)
        np.testing.assert_array_equal(result.data, expected)

    def test_mul(self):
        tensor1 = Tensor([[1, 2], [3, 4]])
        tensor2 = Tensor([[5, 6], [7, 8]])
        result = tensor1.mul(tensor2)
        expected = np.array([[5, 12], [21, 32]], dtype=np.float32)
        np.testing.assert_array_equal(result.data, expected)

    def test_dot(self):
        tensor1 = Tensor([[1, 2], [3, 4]])
        tensor2 = Tensor([[5, 6], [7, 8]])
        result = tensor1.dot(tensor2)
        expected = np.array([[19, 22], [43, 50]], dtype=np.float32)
        np.testing.assert_array_equal(result.data, expected)

    def test_transpose_1d(self):
        tensor = Tensor([1, 2, 3])
        transposed = tensor.transpose()
        # 1D tensor transpose is itself
        expected = np.array([1, 2, 3], dtype=np.float32)
        np.testing.assert_array_equal(transposed.data, expected)

    def test_transpose_2d(self):
        tensor = Tensor([[1, 2, 3], [4, 5, 6]])
        transposed = tensor.transpose()
        expected = np.array([[1, 4], [2, 5], [3, 6]], dtype=np.float32)
        np.testing.assert_array_equal(transposed.data, expected)

    def test_linear(self):
        x = Tensor([[1, 2], [3, 4]])
        weight = Tensor([[1, 0], [0, 1]])
        bias = Tensor([1, 1])
        result = x.linear(weight, bias)
        expected = np.array([[2, 3], [4, 5]], dtype=np.float32)
        np.testing.assert_array_equal(result.data, expected)

    def test_linear_no_bias(self):
        x = Tensor([[1, 2], [3, 4]])
        weight = Tensor([[1, 0], [0, 1]])
        result = x.linear(weight, None)
        expected = np.array([[1, 2], [3, 4]], dtype=np.float32)
        np.testing.assert_array_equal(result.data, expected)

    def test_mutation(self):
        tensor = Tensor([[1, 2, 3], [4, 5, 6]])
        tensor.data[1, 1] = 10
        self.assertTrue(np.array_equal(tensor.data, [[1, 2, 3], [4, 10, 6]]))

    def test_shape_calculation(self):
        tensor_1d = Tensor([1, 2, 3])
        self.assertEqual(tensor_1d.shape, (3,))


if __name__ == '__main__':
    unittest.main()
