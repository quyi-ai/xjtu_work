from random import randint
from math import gcd
min_value, max_value = 1, 1000
gcd_case = []
times = 100
for _ in range(times):
    n = randint(min_value, max_value)
    m = randint(min_value, max_value)
    gcd_case.append((m, n))


def hw_gcd(m, n):
    m, n = max(m, n), min(m, n)
    if n == 1:
        return n
    elif n == 0:
        return m
    else:
        return hw_gcd(m % n, n)


for m, n in gcd_case:
    assert hw_gcd(m, n) == gcd(m, n)
print("hyw")
