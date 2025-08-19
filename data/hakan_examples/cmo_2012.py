#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/2012_CMO_problem.py

"""Given two positive integers a and b, where a - b is a prime number and a × b is a perfect square n^2,
find the smallest value of a no less than 2012.

Print the values of a, b, n, and p (a, b, n, p).
"""

# Import libraries
from cpmpy import *
import json
from math import sqrt


def is_prime(n):
    """Return True if n is prime, False otherwise"""
    if n < 2:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def primes(n):
    """Return a list of primes less than n"""
    primes = []
    for i in range(2, n):
        if is_prime(i):
            primes.append(i)
    return primes


max_val = 10000
prime_list = primes(2012)

a = intvar(2012, max_val, name="a")
b = intvar(2, 2012, name="b")
n = intvar(2, 2012, name="n")
# p can only take primes (reduced below).
# How do one create a list of specific domain in cpmpy?
p = intvar(2, 2012, name="p")

model = Model(minimize=a)

for i in range(max(prime_list)):
    # if not i in prime_list:
    #  model += [p != i]
    if not is_prime(i):
        model += [p != i]

model += [a >= b]
model += [p == a - b]
model += [a * b == n * n]

model.solve()

solution = {"a": a.value(), "b": b.value(), "n": n.value(), "p": p.value()}
print(json.dumps(solution))
# End of CPMPy script
