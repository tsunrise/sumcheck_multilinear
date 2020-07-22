from unittest import TestCase
from multilinear_extension import extend, extend_sparse, evaluate, evaluate_sparse
import random
from polynomial import randomPrime


class Test(TestCase):
    def test_extend(self):
        for t in range(10):
            p = randomPrime(64)
            arr = [random.randint(0, p-1) for _ in range(1024)]
            poly = extend(arr, p)
            for _ in range(poly.num_variables ** 2):
                i = random.randint(0, len(arr)-1)
                self.assertEqual(arr[i], poly.eval_bin(i))
            print(f"Test #{t} finished. ")

    def test_extend_sparse(self):
        for t in range(10):
            p = randomPrime(64)
            L = 10
            data = {random.randint(0, (1 << L) - 1): random.randint(0, p-1) for _ in range(256)}
            poly = extend_sparse(data, L, p)
            for k in range((1 << L) - 1):
                expected = data[k] if k in data else 0
                actual = poly.eval_bin(k)
                self.assertEqual(expected, actual)
            print(f"Test #{t} finished. ")

    def test_evaluate(self):
        for t in range(10):
            p = randomPrime(64)
            L = 8
            arr = [random.randint(0, p-1) for _ in range(1 << L)]
            poly = extend(arr, p)
            args = [random.randint(0, p-1) for _ in range(L)]
            self.assertEqual(poly.eval(args), evaluate(arr, args, p))

    def test_evaluate_sparse(self):
        for t in range(10):
            p = randomPrime(64)
            L = 9
            data = {random.randint(0, (1 << L) - 1): random.randint(0, p-1) for _ in range(1 << round(L**0.5))}
            poly = extend_sparse(data, L, p)
            args = [random.randint(0, p - 1) for _ in range(L)]
            self.assertEqual(poly.eval(args), evaluate_sparse(data, args, p))
