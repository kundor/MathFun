#!/usr/bin/awk -f
BEGIN {i=1; p = 2}
!/i/ {
    printf "%14d/%-14d = %.7f, %16d/%-16d = %.7f\n", $1, i, ($1/i), $3, p, ($3/p)
    i=$1
    p=$3
} 

