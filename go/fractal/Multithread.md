The fractal generation is embarrassingly parallel, since it just iterates each pixel's coordinates separately
till it finds its destination, so it's an easy win to split it into goroutines by pixel.

The fastest method is to keep a global image.RGBA, and have each goroutine set pixel colors.
This is safe (https://stackoverflow.com/questions/49879322/can-i-concurrently-write-different-slice-elements).

However, it's not safe with the arbitrary integer polynomial fractal functions returned by
NewPolyFractal(coefs). Those tracks the polynomial roots as they are found in a slice `roots`
wrapped in the closure. Having different goroutines calling roots = append(roots, z) is a race.

A mutex lock was added around checking the roots, which will reduce the benefits of parallelization.

Timings:
For a single request at a time, paralellization improved times:
Mandelbrot: 0.2s to 0.1s
7th roots of unity: 2.1s to 0.8s
Newton fractal for 2-2x+x^3: 0.45s to 0.2s

The Newton fractal is the one requiring the mutex lock around the roots access,
so even with that contention the speedup is considerable.

The outputs for the Newton fractal have different colors, however, since the order of root discovery changes.
It is deterministic for a single-threaded program.

For handling five requests at once, the benefits are less, as you might expect.
The following times are for the last request to complete when five are started simulteneously.
Mandelbrot: 0.36s to 0.32s
7th roots of unity: 3.0s to 2.5s
Newton fractal for 2-2x+x^3: 0.7s to 0.6s
