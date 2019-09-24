def basecoef(num, base):
    """List of coefficients [c_0, c_1, ..., c_k] so num = Σ c_i * base**i"""
    digs = []
    while num:
        num, dig = divmod(num, base)
        digs.append(dig)
    return digs

def bctoint(digs, base):
    return sum(ci*base**i for i,ci in enumerate(digs))

def weak_goodstein(n):
    base = 2
    yield n
    while n:
        n = bctoint(basecoef(n, base), base+1) - 1
        base += 1
        yield n

def heredbase(num, base):
    """Express num in the given base, with exponents also expressed in the base"""
    if num < base:
        return str(num)
    ans = ''
    p = 0
    while num:
        num, cp = divmod(num, base)
        if cp and p >= base:
            ans += f'{cp}*{base}**({heredbase(p, base)}) + '
        elif cp:
            ans += f'{cp}*{base}**{p} + '
        p += 1
    return ans[:-3]

def goodstein(n):
    base = 2
    yield n
    while n:
        hb = heredbase(n, base)
        hb = hb.replace(f'*{base}**', f'*{base+1}**')
        n = eval(hb) - 1
        base += 1
        yield n

def goodstein_sub(n):
    """
    Variant of the Goodstein sequence, subtracting 1 before bumping the base.
    Seen in Schwichtenberg and Wainer _Proofs and Computations_; A222112, A222113.
    """
    base = 2
    yield n
    while n:
        hb = heredbase(n-1, base).replace(f'*{base}**', f'*{base+1}**')
        n = eval(hb)
        base += 1
        yield n

def print_sequence(seq, offset=0, maxdigit=999, maxindex=10000):
    """
    Produce output appropriate for OEIS b-file:
    n a_n
    separated by single space, starting with n=0 or n=2, max length 1000 digits
    """
    for i, n in enumerate(seq, start=offset):
        if i > maxindex or n >= 10**maxdigit:
            break
        print(f'{i} {n}')

def seqchars(seq, nchar, join=', ', init=''):
    """Return first string with length >= nchar with terms from the given sequence"""
    seq = iter(seq)
    dat = init or str(next(seq))
    while len(dat) < nchar:
        dat += f'{join}{next(seq)}'
    return dat

def datastring(n, nchar=260):
    """Return nchar characters worth of the Goodstein sequence"""
    dat = seqchars(goodstein(n), nchar)
    # dat could be too long. Allow "overage" as long as omitting spaces brings it under
    if len(dat) - dat.count(' ') < nchar:
        return dat
    return ', '.join(dat.split(', ')[:-1]) # omit last term

if __name__ == "__main__":
    import sys
    if len(sys.argv) not in {2,3}:
        sys.exit('Must give a starting number, and optionally a starting index (for numbering purposes only)')
    num = int(sys.argv[1])
    offset = 0
    if len(sys.argv) > 2:
        offset = int(sys.argv[2])
    print_sequence(goodstein(num), offset)


