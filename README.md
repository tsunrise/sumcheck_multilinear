# Sumcheck protocol for Multilinear polynomials
A python implementation of sumcheck protocol for multilinear polynomials. Sumcheck protocol is useful in interactive proofs (IP). 

## Getting Started

### Represent a multilinear polynomial

Each multilinear polynomial is an instance of `MVLinear` class. We need to specify the number of variables in the polynomial, the coefficient of each monomial, and the size of the finite field of this polynomial. Example: 

```python
# P(x0, x1, x2, x3) = 15 + x0 + 4*x3 + x1*x2 + 5*x2*x3 (in Z_37)
P = MVLinear(4, {0b0000: 15, 0b0001: 1, 0b1000: 4, 0b0110: 1, 0b1100: 5}, 37)
```

The monomials are represented by a dictionary where the index is the binary form of the monomial: the least significant bit represents `x0`, second least significant bit represents `x1` and so on. The value represents the coefficient of the monomial. 

We can add, subtract, and multiply polynomials using python `+`, `-`, `*` operators. For multiplication, if the result polynomial is no longer multilinear, an `ArithmeticError` will be raised. 

We can also use `makeLinearConstructor` to generate polynomials with same number of variables and field size quickly. This function takes `num_variables` and `p` (field size) and return a function that takes monomials and return the `MVLinear` instance. 

Examples for polynomial operations: 

```python
m = makeMVLinearConstructor(4, 37)
x0 = m({0b1: 1})
x1 = m({0b10: 1})
x2 = m({0b100: 1})
x3 = m({0b1000: 4})
x4 = m({0b10000: 5})

p = 2*x2 + 3*x3 + 19
p2 = x1 + 7*x0*x1+ x0 + 8
p  # MVLinear( + 2*x2 + 12*x3 + 19)
p2  # MVLinear( + 1*x1 + 7*x0x1 + 1*x0 + 8)
p+p2 # MVLinear( + 2*x2 + 12*x3 + 27 + 1*x1 + 7*x0x1 + 1*x0)
p-p2 # MVLinear( + 2*x2 + 12*x3 + 11 + 36*x1 + 30*x0x1 + 36*x0)
p*p2  # MVLinear( + 2*x1x2 + 14*x0x1x2 + 2*x0x2 + 16*x2 + 12*x1x3 + 10*x0x1x3 + 12*x0x3 + 22*x3 + 19*x1 + 22*x0x1 + 19*x0 + 4)
p*p # ArithmeticError: no longer multilinear
```

### Initialize the Interactive Verifier

The constructor of the verifier takes `seed` (random source), `polynomial` (the multilinear polynomial to check), `asserted_sum` (the sum that the prover is going to prove). At the beginning, the verifier is not convinced. When the prover calls prove and send the verifier a univariate linear polynomial (represented by P(0) and P(1)), the verifier verifies the sum, sends a random value back, and goes to next round. 

Example: 

```python
p = 2*x0 + 3 * x1 + 3
v = InteractiveVerifier(12345, p, 22)  # v.active = True, v.convinced = False
v.prove(p(0,0)+p(0,1), p(1,0)+p(1,1))  # returns (True, 26), v.active = True, v.convinced = False
v.prove(p(26, 0), p(26, 1))  # returns (True, 0), v.active = False, v.convinced = True
# Verifier accepts the result
```

## Todo List

- Completed: A sparse representation and evaluation oracle for multilinear function. 
- Completed: An Interactive Verifier. 
- Completed: A naïve prover, taking O(n*2^n) time. 
- Completed: A faster prover using dynamic programming taking O(2^n) time. (Reference: Xie, Zhang, Zhang, Papamanthou, Song, 2019, https://eprint.iacr.org/2019/317.pdf)
- Todo: A non-interactive verifier using random oracle based on SHA256 (using Fiat-Shamir Transform). 
- TBD

![image-20200625132007528](assets/image-20200625132007528.png)