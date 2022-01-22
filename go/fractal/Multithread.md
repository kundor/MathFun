The fractal generation is embarrassingly parallel, since it just iterates each pixel's coordinates separately
till it finds its destination, so it's an easy win to split it into goroutines by pixel.

The fastest method is to keep a global image.RGBA, and have each goroutine set pixel colors.
This is safe (https://stackoverflow.com/questions/49879322/can-i-concurrently-write-different-slice-elements).

However, it's not safe with the arbitrary integer polynomial fractal functions returned by
NewPolyFractal(coefs). Those tracks the polynomial roots as they are found in a slice `roots`
wrapped in the closure. Having different goroutines calling roots = append(roots, z) is a race.
