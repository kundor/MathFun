#include <cstdio>
#include <NTL/ZZ.h>

int main() {
    unsigned long i = 0, N = 6, p = 1;
    char c;
    while (i < 100) {
        p = NTL::NextPrime(p + 1);
        if (p > N) {
            N += p;
            c = '+';
        } else {
            N -= p;
            c = '-';
        }
        ++i;
        printf("%lu. %c%lu: %lu\n", i, c, p, N);
    }
    return 0;
}


