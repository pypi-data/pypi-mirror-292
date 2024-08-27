import unittest
from kriknn.nn import Linear
from kriknn.engine.tensor import Tensor
import numpy as np


class TestLinear(unittest.TestCase):
    def test_linear_initialization(self):
        features_in = 4
        features_out = 3
        linear_layer = Linear(features_in, features_out)

        # Validate that the weights and bias are initialized correctly
        self.assertEqual(linear_layer.weight.shape,
                         (features_in, features_out))
        if linear_layer.bias is not None:
            self.assertEqual(linear_layer.bias.shape, (features_out,))

        # Ensure weights are within the expected range
        bound = 1 / np.sqrt(features_in)
        for row in linear_layer.weight.data:
            for value in row:
                self.assertGreaterEqual(value, -bound)
                self.assertLessEqual(value, bound)

        # Ensure bias is within the expected range
        if linear_layer.bias is not None:
            for value in linear_layer.bias.data:
                self.assertGreaterEqual(value, -bound)
                self.assertLessEqual(value, bound)

    def test_linear_forward_pass(self):
        features_in = 4
        features_out = 2
        linear_layer = Linear(features_in, features_out)

        # Create a sample input tensor
        input_data = [[1.0, 2.0, 3.0, 4.0]]
        x = Tensor(input_data)

        # Perform the forward pass
        output = linear_layer(x)

        # Validate the output shape
        self.assertEqual(output.shape, (1, features_out))


if __name__ == '__main__':
    unittest.main()
