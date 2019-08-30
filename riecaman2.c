#include <stdio.h>
#include <gmp.h>

/* Using gmp here is probably not necessary
 * Since about 416,000,000,000,000,000 (416 quadrillion) primes fit in 64 bits
 * and we can only progress a few billion steps in a reasonable time.
 * So all the primes will fit in 64 bits, and N won't get much larger than the primes.
 * But nextprime is in gmp... */

int main() {
    unsigned long i = 0;
    mpz_t N, p;
    mpz_init_set_ui(N, 6ul);
    mpz_init(p);
    while (mpz_sgn(N)) {
        mpz_nextprime(p, p);
        if (mpz_cmp(p, N) > 0) {
            mpz_add(N, N, p);
        } else {
            mpz_sub(N, N, p);
        }
        ++i;
        if (!(i & 0xFFFFFul)) {
            gmp_printf("%lu. %Zd: %Zd\n", i, p, N);
            if (i > 10000000) {
                break;
            }
        }
    }
    return 0;
}


