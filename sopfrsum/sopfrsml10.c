#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <gmp.h>

#define MAXN 50000000u

// time for 500000 with ui_pow_ui: 2m28s
// time for 500000 with nn * nnnn * nnnn: 2m32s

mpz_t *primes;
int nprimes;
int primecap;

bool sopfrsml(mpz_t sopr, const mpz_t bignum, unsigned long n) {
    mpz_t tmp;
    mpz_init_set(tmp, bignum);
    mpz_set_ui(sopr, 0u);
    for (mpz_t *p = primes; p < primes+nprimes; ++p) {
        if (mpz_cmp_ui(*p, n) >= 0)
            break; 
        while (mpz_divisible_p(tmp, *p)) {
            mpz_add(sopr, sopr, *p);
            mpz_divexact(tmp, tmp, *p);
            if (mpz_cmp_ui(sopr, n) > 0) {
                 return false;
            }
            if (mpz_cmp_ui(tmp, 1u) == 0)
                return true;
        }
    }
    if (mpz_cmp_ui(tmp, 1u) > 0)
        return false;
    return true;
}

int main() {
    primecap = 3<<20; // 3,145,728; enough to hold all primes up to 50 million
    primes = malloc(primecap * sizeof(mpz_t));
    mpz_init_set_ui(primes[0], 2u);
    nprimes = 1;
    while (mpz_cmp_ui(primes[nprimes-1], MAXN) < 0) {
        if (nprimes >= primecap) {
            primecap *= 2;
            primes = realloc(primes, primecap * sizeof(mpz_t));
            if (!primes) {
                perror("Oh no couldn't allocate space for primes");
                return 1;
            }
        }
        mpz_init(primes[nprimes]);
        mpz_nextprime(primes[nprimes], primes[nprimes-1]);
        ++nprimes;
    }
    gmp_printf("%d primes / %d space, last one %Zd\n", nprimes, primecap, primes[nprimes-1]);
   
    mpz_t sumpow, sopr, ntok;
    mpz_init(sumpow);
    mpz_init(sopr);
    mpz_init(ntok);
    int nbig, nsmall;
    unsigned long soprui;

    printf("10th powers\n");
    mpz_set_ui(sumpow, 1u);
    nbig = nsmall = 0;
    for (unsigned long n = 2; n <= MAXN; ++n) {
        mpz_ui_pow_ui(ntok, n, 10);
        mpz_add(sumpow, sumpow, ntok);
        if (sopfrsml(sopr, sumpow, n)) {
            soprui = mpz_get_ui(sopr);
            if (soprui < n - 2) {// n >= 2, so n-2 >= 0, no wraparound
                ++nsmall;
                if (nsmall < 12)
                    gmp_printf("Small: g(f(%lu, 10)) = g(%Zd) = %lu\n", n, sumpow, soprui);
            }
            else if (soprui < n) {
                gmp_printf("Near miss: g(f(%lu, 10)) = g(%Zd) = %lu\n", n, sumpow, soprui);
            }
            else if (soprui > n)
                ++nbig;
            else {
                gmp_printf("g(f(%lu, 10)) = g(%Zd) = %lu\n", n, sumpow, soprui);
            }
        } else { // sum of prime factors would be bigger than n
            ++nbig;
        }
        if (!(n & 0x7FFFFu)) {
            printf("n %lu, %d small, %d big\n", n, nsmall, nbig);
        }
    }
    printf("Total: %d small, %d big\n", nsmall, nbig);
    
    return 0;
}
