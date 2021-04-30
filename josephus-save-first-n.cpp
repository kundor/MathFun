/* See josephus-save-first-n.py for extended description.
 * Direct "simulation" approach: remove every qth element from a vector
 * until only n are left. If we kill any "good guy" (1 to n), then return false. */

#include <cstdio>
#include <vector>
#include <numeric>

bool firstn(int n, long q) {
    int i = 0, size = 2*n;
    std::vector<int> circle(2*n);
    std::iota(circle.begin(), circle.end(), 1); // fill 1...2n
    while (size > n) {
        i = (i + q - 1) % size;
        if (circle[i] <= n)
            return false;
        circle.erase(circle.begin() + i);
        --size;
    }
    return true;
}
/* With vector, up to n=16, at -O3: 3.93 s */

int main() {
    int n;
    long q;
    for (n = 1; n < 23; ++n) {
        for (q = n + 1; !firstn(n, q); ++q);
        std::printf("%2i: %li\n", n, q);
    }
    return 0;
}
