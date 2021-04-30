# minimal extract of josephus-save-first-n.py for inclusion in OEIS

def savesfirstn(n, q):
    circle = list(range(2*n))
    i = 0
    while len(circle) > n:
        i = (i + q - 1) % len(circle)
        if circle[i] < n:
            return False
        del circle[i]
    return True
for n in range(1, 22):
    q = n + 1
    while not savesfirstn(n, q):
        q += 1
    print(n, q)
