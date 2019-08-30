#include <cstdio>
#include <primesieve.hpp>

int main() {
    unsigned long i = 0, N = 6, p = 1;
    primesieve::iterator it;
    bool isodd = N % 2;
    if (!isodd) {
        if (N == 0) {
            printf("0 steps\n");
            return 0;
        }
        if (N == 2) {
            printf("1 step, last prime 2\n");
            return 0;
        }
        p = it.next_prime();
        if (p > N) {
            N += p;
        } else {
            N -= p;
        }
    }
    for (;;) {
        /* N starts even (or n_0 odd) */
        p = it.next_prime();
        if (p > N) {
            N += p;
        } else {
            N -= p;
        }
        /* N is odd after adding/subtracting one prime */
        p = it.next_prime();
        if (p > N) {
            N += p;
        } else {
            N -= p;
            if (!N) // this is the only case we can get N to 0
                break;
        }
        /* Now N is even again */
        ++i;
        if (!(i & 0xFFFFFFFul)) {
            printf("%lu. %lu: %lu\n", 2*i, p, N);
        }
    }
    printf("%lu steps, last prime %lu\n", i, p);
    return 0;
}


