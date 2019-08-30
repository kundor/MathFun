#include <stdio.h>
#include <gmp.h>

int main() {
    unsigned long i = 0;
    mpz_t N, p;
    mpz_init_set_ui(N, 6ul);
    mpz_init(p);
    char c;
    while (i < 100) {
        mpz_nextprime(p, p);
        if (mpz_cmp(p, N) > 0) {
            mpz_add(N, N, p);
            c = '+';
        } else {
            mpz_sub(N, N, p);
            c = '-';
        }
        ++i;
        gmp_printf("%lu. %c%Zd: %Zd\n", i, c, p, N);
    }
    return 0;
}


