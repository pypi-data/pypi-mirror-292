import unittest
import numpy as np
from deming_regression import deming_regression

class TestDemingRegression(unittest.TestCase):
    def test_perfect_line(self):
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 1
        intercept, slope = deming_regression(x, y, 0.1, 0.1)
        self.assertAlmostEqual(intercept, 1, places=2)
        self.assertAlmostEqual(slope, 2, places=2)

    def test_noisy_data(self):
        np.random.seed(42)
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 1 + np.random.normal(0, 0.1, 5)
        intercept, slope = deming_regression(x, y, 0.1, 0.1)
        self.assertAlmostEqual(intercept, 1, places=1)
        self.assertAlmostEqual(slope, 2, places=1)

    def test_different_noise_levels(self):
        np.random.seed(42)
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 1 + np.random.normal(0, 0.2, 5)
        intercept1, slope1 = deming_regression(x, y, 0.1, 0.1)
        intercept2, slope2 = deming_regression(x, y, 0.1, 0.2)
        self.assertNotEqual(intercept1, intercept2)
        self.assertNotEqual(slope1, slope2)
