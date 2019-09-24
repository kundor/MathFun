/*-*- compile-command: "cc -c -o stdin.o -g -O3 -Wall -fomit-frame-pointer -fno-strict-aliasing -fPIC -I\"/usr/include/x86_64-linux-gnu\" stdin.c && cc -o stdin.so -shared -g -O3 -Wall -fomit-frame-pointer -fno-strict-aliasing -fPIC -Wl,-shared -Wl,-z,relro stdin.o -lc -lm -L/usr/lib/x86_64-linux-gnu -lpari"; -*-*/
#include <pari/pari.h>

static GEN M;
/*End of global vars*/

int main(void) {
  M = pol_x(fetch_user_var("M"));
  {
    long k;
    for (k = 1; k <= 9; ++k)
    {
      long n;
      for (n = 2; n <= 19999; ++n)
      {
        GEN p1;
        {
          long i;
          p1 = gen_0;
          for (i = 1; i <= n; ++i)
            p1 = gadd(p1, powis(stoi(i), k));
        }
        M = factorint(p1, 0);
        if (gequalgs(gmul(gtrans(gel(M, 1)), gel(M, 2)), n))
          pari_printf("%ld%ld\n", n, k);
      }
    }
  }
  return 0;
}

