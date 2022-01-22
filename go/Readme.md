This is a combination and extension of exercises 1.6, 1.12, 3.2, 3.4, 3.5, 3.7, and 3.9
of [The Go Programming Language](https://gopl.io).
The main extensions are

* Taking an arbitrary function for the 3D surface plotter. Rather than implementing a parser, it is fed to a `bc` process.

* From 3.7 (coloring the complex plane by the number of iterations of Newton's method to reach a root of z^4-1) to take
  an arbitrary integer-coefficient polynomial.

Do not run this server on the open internet; there is probably remote execution vulnerability (because it passes
the input formula to `bc`.)
