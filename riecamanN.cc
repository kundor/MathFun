#include <cstdio>
#include <cstdlib>
#include <csignal>
#include <primesieve.hpp>

static volatile std::sig_atomic_t interrupted = 0;
static unsigned long steps, p, q, qmp, startN, N;
static primesieve::iterator it;

void signal_handler(int signal) {
    interrupted = signal;
}

inline static void incrsteps() {
    steps += 2;
    if (!(steps & 0x1FFFFFFFEul)) {
        printf("%lu. %lu: %lu\n", steps, q, N);
    }
    if (interrupted) {
        printf("%lu: >%lu steps, last prime %lu, last value %lu\n", startN, steps, q, N);
        if (interrupted != SIGHUP)
            exit(1);
        else {
            interrupted = 0;
            std::signal(SIGHUP, signal_handler);
        }
    }
}

inline static void endit() {
    printf("%lu: %lu steps, last prime %lu\n", startN, steps, q);
    exit(0);
}

inline static void descent() {
    for (;;) {
        /* Precondition: N is less than p */
        p = it.next_prime();
        q = it.next_prime();
        qmp = q - p;
        if (N <= qmp) {
            break;
        }
        N -= qmp;
        incrsteps();
        /* Postcondition: N same parity, even smaller */
    }
    if (N == qmp) {
        steps += 2;
        endit();
    }
    printf("Min at step %lu: %lu; + %lu = Arc max %lu; + %lu = %lu\n",
            steps, N, p, N + p, q, N + p + q);
    N += p + q;
    /* N is big. */
    p = it.next_prime();
    N -= p;
    steps += 3;
    /* Now N is small and opposite parity. */
}

int main(int argc, char** argv) {
    setvbuf(stdout, NULL, _IOLBF, BUFSIZ);
    if (argc == 5) {
        steps = std::atol(argv[2]);
        N = std::atol(argv[3]);
        p = std::atol(argv[4]);
        it.skipto(p);
    } else if (argc != 2) {
        std::fputs("Exactly one or four arguments required: initial value for N;\n"
                   " if resuming, also <step> <last value> <last prime>.\n", stderr);
        std::exit(1);
    }

    startN = std::atol(argv[1]);

    if (argc == 2) {
        steps = 0;
        N = startN;
        if (N == 2) {
            printf("2: 1 step, last prime 2\n");
            return 0;
        }
    }

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);
    std::signal(SIGHUP, signal_handler);

    /* Initial descent */
    for (;;) {
        p = it.next_prime();
        if (N <= p) break;
        N -= p;
        ++steps;
    }
    if (N == p) {
        ++steps;
        q = p;
        endit();
    }
    printf("Initial descent to %lu in %lu steps; first increase %lu\n", N, steps, p);
    N += p;
    q = it.next_prime();
    steps += 2;
    if (N >= q) {
        N -= q;
        /* N is small, good to go */
    } else {
        printf("...was a min; + %lu = arc max %lu; + %lu = %lu\n",
                p, N, q, N + q);
        N += q;
        /* N is big */
        q = it.next_prime();
        N -= q;
        ++steps;
        /* Now N is small. (Sum of any two consecutive primes is >= next prime, right?) */
    }
    
    if (!N) {
        endit();
    }

    for (;;) {
        descent();
    }
}


