#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <gmp.h>

#define MAXN 1000000u
#define MAXPOW 100

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
    primecap = 100000;
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
   
    mpz_t sumpow, ntok, sopr;
    mpz_init(sumpow);
    mpz_init(ntok);
    mpz_init(sopr);
    int nbig, nsmall;
    unsigned long soprui;
    bool newline;

    for (unsigned long k = 55; k <= MAXPOW; ++k) {
        printf("%lu", k);
        newline = false;
        mpz_set_ui(sumpow, 1u);
        nbig = nsmall = 0;
        for (unsigned long n = 2; n <= MAXN; ++n) {
            mpz_ui_pow_ui(ntok, n, k);
            mpz_add(sumpow, sumpow, ntok);
            if (sopfrsml(sopr, sumpow, n)) {
                soprui = mpz_get_ui(sopr);
                if (soprui < n - 2) // n >= 2, so n-2 >= 0, no wraparound
                    ++nsmall;
                else if (soprui < n) {
                    gmp_printf("\nNear miss: g(f(%lu, %lu)) = g(%Zd) = %lu", n, k, sumpow, soprui);
                    newline = true;
                }
                else if (soprui > n)
                    ++nbig;
                else {
                    gmp_printf("\ng(f(%lu, %lu)) = g(%Zd) = %lu", n, k, sumpow, soprui);
                    newline = true;
                }
            } else { // sum of prime factors would be bigger than n
                ++nbig;
            }
/*            if (n == 21u) {
                gmp_printf("n %lu, k %lu, sum powers %Zd, sopfr %Zd, cmpn %d\n", n, k, sumpow, sopr, cmpn);
            }*/
        }
        if (newline)
            printf("\n ");
        printf("...%d small, %d big\n", nsmall, nbig);
    }
    return 0;
}
