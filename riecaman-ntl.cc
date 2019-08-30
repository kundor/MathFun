#include <cstdio>
#include <NTL/ZZ.h>

int main() {
    unsigned long i = 0, N = 6, p = 1;
    while (N) {
        p = NTL::NextPrime(p + 1);
        if (p > N) {
            N += p;
        } else {
            N -= p;
        }
        ++i;
        if (!(i & 0xFFFFFul)) {
            printf("%lu. %lu: %lu\n", i, p, N);
            if (i > 10000000) {
                break;
            }
        }
    }
    return 0;
}


