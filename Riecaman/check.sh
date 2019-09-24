diff -s hv-results <(for n in {0..100}; do timeout 1 ./riecamanN $n; done | awk '/^[0-9]*: [0-9]* steps?/ {sub(":", " ", $1); print $1 $2} /^[0-9]*: >/ {sub(":", " ", $1); print $1 "unknown"}')

