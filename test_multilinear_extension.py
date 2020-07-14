from unittest import TestCase
from multilinear_extension import extend
import random
from polynomial import randomPrime


class Test(TestCase):
    def test_extend(self):
        for t in range(10):
            p = randomPrime(64)
            arr = [random.randint(0, p-1) for _ in range(6000)]
            poly = extend(arr, p)
            for _ in range(poly.num_variables ** 2):
                i = random.randint(0, len(arr)-1)
                self.assertTrue(arr[i], poly.eval_bin(i))
            print(f"Test #{t} finished. ")
