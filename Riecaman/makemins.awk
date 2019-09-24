#!/usr/bin/awk -f
BEGIN {printf "%13s %3s %14s\n", "i", "n_i", "p_{i+1}"}
/Min/ {printf "%13d %3d %14d\n", $4, $5, $7}
