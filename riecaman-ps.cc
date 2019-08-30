#include <cstdio>
#include <primesieve.hpp>

int main() {
    unsigned long i = 0, N = 6, p = 1;
    primesieve::iterator it;
    while (N) {
        p = it.next_prime();
        if (p > N) {
            N += p;
        } else {
            N -= p;
        }
        ++i;
        if (!(i & 0x7FFFFFFul)) {
            printf("%lu. %lu: %lu\n", i, p, N);
        }
    }
    printf("%lu steps, last prime %lu\n", i, p);
    return 0;
}


