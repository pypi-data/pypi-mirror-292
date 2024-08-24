import unittest
from src.core import LAMBDA, LambdaWrapper

class TestExtendedLambda(unittest.TestCase):
    def test_lambda_pass(self):
        double = LAMBDA >> (lambda x: x * 2)
        self.assertEqual(double(5), 10)

    def test_lambda_return(self):
        triple = LAMBDA << (lambda x: x * 3)
        self.assertIsInstance(triple(5), LambdaWrapper)
        self.assertEqual(triple(5)(), 15)

if __name__ == '__main__':
    unittest.main()