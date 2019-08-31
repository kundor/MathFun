#include <cstdio>
#include <cstdlib>
#include <csignal>
#include <primesieve.hpp>

static volatile std::sig_atomic_t interrupted = 0;

inline static void addsub(primesieve::iterator& pit, unsigned long& N, unsigned long& p) {
    p = pit.next_prime();
    if (p > N) {
        N += p;
    } else {
        N -= p;
    }
}

void signal_handler(int signal) {
    interrupted = 1;
}

int main(int argc, char** argv) {
    unsigned long i = 0, p = 1, startN, N;
    primesieve::iterator it;
    if (argc == 5) {
        i = std::atol(argv[2]);
        N = std::atol(argv[3]);
        p = std::atol(argv[4]);
        it.skipto(p);

        if (N % 2) {
            addsub(it, N, p);
            ++i;
        }
        i /= 2;
    } else if (argc != 2) {
        std::fputs("Exactly one or four arguments required: initial value for N;\n"
                   " if resuming, also <step> <last value> <last prime>.\n", stderr);
        std::exit(1);
    }

    startN = std::atol(argv[1]);
    bool isodd = startN % 2;

    if (argc == 2) {
        N = startN;
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
    }

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

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
        if (!(i & 0xFFFFFFFul) || interrupted) {
            printf("%lu. %lu: %lu\n", 2*i + !isodd, p, N);
            if (interrupted)
                return 1;
        }
    }
    printf("%lu: %lu steps, last prime %lu\n", startN, 2 + 2*i + !isodd, p);
    return 0;
}


