from random import randint
from math import gcd
min_value, max_value = 1, 1000

times = 100
pow_case = [randint(min_value, max_value) for _ in range(100)]


def hw_pow(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    return hw_pow(n//2)*10+n % 2


for i, n in enumerate(pow_case, 1):
    expected = int(bin(n)[2:])
    result = hw_pow(n)
    assert result == expected
print("hyw")
