#include <cstdio>
#include <cstdlib>
#include <primesieve.hpp>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fputs("Exactly one argument required: initial value for N\n", stderr);
        std::exit(1);
    }
    unsigned long i = 0, p = 1, N;
    N = std::atol(argv[1]);
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


