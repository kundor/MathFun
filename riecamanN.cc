#include <cstdio>
#include <cstdlib>
#include <primesieve.hpp>

inline static void addsub(primesieve::iterator& pit, unsigned long& N, unsigned long& p) {
    p = pit.next_prime();
    if (p > N) {
        N += p;
    } else {
        N -= p;
    }
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fputs("Exactly one argument required: initial value for N\n", stderr);
        std::exit(1);
    }
    unsigned long i = 0, p = 1, startN, N;
    N = startN = std::atol(argv[1]);
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
        addsub(it, N, p);
    }

    for (;;) {
        /* N starts even (or n_0 odd) */
        addsub(it, N, p);
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
            printf("%lu. %lu: %lu\n", 2*i + !isodd, p, N);
        }
    }
    printf("%lu: %lu steps, last prime %lu\n", startN, 2 + 2*i + !isodd, p);
    return 0;
}


