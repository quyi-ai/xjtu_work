def add(a, b):
    n = max(len(a), len(b))
    res = [0] * n
    for i in range(n):
        va = a[i] if i < len(a) else 0
        vb = b[i] if i < len(b) else 0
        res[i] = va + vb
    return res

def sub(a, b):
    n = max(len(a), len(b))
    res = [0] * n
    for i in range(n):
        va = a[i] if i < len(a) else 0
        vb = b[i] if i < len(b) else 0
        res[i] = va - vb
    return res

def Karatsuba(a, b):
    if not a or not b:
        return [0]
    
    n = max(len(a), len(b))
    if n == 1:
        return [a[0] * b[0]]
    a = a + [0] * (n - len(a))
    b = b + [0] * (n - len(b))
    
    m = n // 2
    a0, a1 = a[:m], a[m:]
    b0, b1 = b[:m], b[m:]
    p1 = Karatsuba(a1, b1)
    p2 = Karatsuba(a0, b0)
    p3 = Karatsuba(add(a0, a1), add(b0, b1))
    mid = sub(sub(p3, p1), p2)
    res = [0] * (2 * n)
    for i in range(len(p2)):
        res[i] += p2[i]
    for i in range(len(mid)):
        res[i + m] += mid[i]
    for i in range(len(p1)):
        res[i + 2 * m] += p1[i]
    while len(res) > 1 and res[-1] == 0:
        res.pop()       
    return res