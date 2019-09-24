import primesieve
import signal

def sigtrunc(n, ndig=2):
    pten = int(log10(n)) - ndig + 1
    if pten < 0:
        return n
    return (n // 10**pten) * 10**pten

quitit = False

def deferint(signum, frame):
    global quitit
    quitit = True

listsize = 1000
listfile = f'list{listsize}'

knownmin = {6: sigtrunc(34883724378113),
           20: sigtrunc(14494027971804),
           50: sigtrunc(2430951489536),
           51: sigtrunc(2413771620352),
           70: sigtrunc(3030206900989),
           92: sigtrunc(2860448219136),
          118: sigtrunc(51539607553),
          119: sigtrunc(51539607553),
          153: sigtrunc(51539607552),
          158: sigtrunc(51539607552),
          188: sigtrunc(51539607553),
          225: sigtrunc(51539607552),
          274: sigtrunc(51539607553),
          322: sigtrunc(51539607552),
          367: sigtrunc(55270046519),
          426: sigtrunc(53697944843),
          429: sigtrunc(52711637523),
          487: sigtrunc(53615087568),
          491: sigtrunc(54278928220),
          498: sigtrunc(53578571870),
          559: sigtrunc(52523334337),
          635: sigtrunc(61203857912),
          702: sigtrunc(56344193395),
          707: sigtrunc(53494306157),
          708: sigtrunc(54650454751),
          869: sigtrunc(53693029487),
          954: sigtrunc(54401351812),
          955: sigtrunc(53637558102),
          956: sigtrunc(52528392832)}

pit = primesieve.Iterator()
traj = []
found = set()
length = []
for x in range(listsize + 1):
    if x in found:
        continue
    sump = 0
    pit.skipto(1)
    starts = {x}
    i = 0
    while sump < listsize - x:
        i += 1
        p = pit.next_prime()
        sump += p
        if x > p:
            x -= p
        elif x < p:
            x += p
            if x + sump <= listsize:
                starts.add(x + sump)
        else:
            length.append(i)
            break
    else: # no break
        length.append(None)
    traj.append(starts)
    found.update(starts)

doit = [min(t) for t,l in zip(traj,length) if l is None]

step = 0
pit.skipto(1)
thelength = {}
startns = doit.copy()
blah = doit.copy()

signal.signal(signal.SIGINT, deferint)
while True:
    p = pit.next_prime()
    step += 1
    torm = []
    for i in range(len(blah)):
        if blah[i] > p:
            blah[i] -= p
        elif blah[i] < p:
            blah[i] += p
        else:
            torm.append(i)
            thelength[startns[i]] = step
            print(f'{startns[i]}: {step}')
    for i in reversed(torm):
        del blah[i]
        del startns[i]
    if quitit:
        break

signal.signal(signal.SIGINT, signal.default_int_handler)
defaultmin = sigtrunc(step)

with open(listfile, 'wt') as lout:
    for n in range(listsize + 1):
        thetraj = next(t for t in traj if n in t)
        minn = min(thetraj)
        tind = traj.index(thetraj)
        if minn in knownmin:
            minstep = knownmin[minn]
        else:
            minstep = defaultmin

        if length[tind] is not None:
            print(f'{n} {length[tind]}', file=lout)
        elif minn in thelength:
            print(f'{n} {thelength[minn]}', file=lout)
        elif n != minn:
            print(f'{n} = a({minn}) > {minstep}', file=lout)
        else: 
            print(f'{n} > {minstep}', file=lout)
