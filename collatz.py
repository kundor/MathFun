def colseq(n):
    while n > 1:
        if n % 2:
            n = 3*n + 1
        else:
            n //= 2
        yield n

# list(colseq(1)) == []
# list(colseq(2)) == [1]
# list(colseq(3)) == [10, 5, 16, 8, 4, 2, 1]

def highest_seq(stop):
    """Return starting integer below stop for Collatz sequence reaching highest max point"""
    return max(range(3, stop), key=lambda i : max(colseq(i)))

# max(range(3,101), key=lambda i: max(colseq(i)) == 27
# max(colseq(27)) == 9232

from collections import deque
from itertools import count

def iterlen(iterseq):
    """Length of iterable"""
#    return sum(1 for _ in iterseq)
    cnt = count()
    deque(zip(iterseq, cnt), 0) # maxlen 0 means it just throws the iterator away
    return next(cnt)
    # Note: sum(1 for _ in seq) : 13 µs for 97; 97.4 ms up to 10000 -> actually slowest 
    #       len(list(seq)):       10.5 µs;      83.3 ms up to 10000 -> actually faster (but consumes memory)
    # cardinality.count:          12.4 µs;      89.2 ms
    # more_itertools.ilen:        12.2 µs;      94.2 ms 
    # deque(zip(it, count()):     10.9 µs;      84 ms   -> very close second, doesn't use memory

def longest_seq(stop):
    """Return starting integer below stop for longest Collatz sequence"""
    return max(range(3, stop), key=lambda i : iterlen(colseq(i)))

# max(range(3,101), key=lambda i: iterlen(colseq(i)) == 97
# iterlen(colseq(97)) == 118

def wherematch(n, m):
    """Indices after which the Collatz sequences for m and n agree."""
    ln = list(colseq(n))
    lm = list(colseq(m))
    ind = max(i for i in range(1, min(len(ln), len(lm))+1) if ln[-i:] == lm[-i:])
    return len(ln) - ind, len(lm) - ind
