//Mandelbrot emits a PNG iamge of the Mandelbrot factorial.
package mandelbrot

import (
	"image"
	"image/color"
	"image/png"
    "io"
    "log"
    "math"
	"math/cmplx"
)

const (
    xmin, ymin, xmax, ymax = -2, -2, +2, +2
    width, height          = 1024, 1024
)

const thresh = 0.0001

type colorfunc func(complex128) color.Color

func WritePNG(w io.Writer, f colorfunc) {
    img := image.NewRGBA(image.Rect(0, 0, width, height))
    for py := 0; py < height; py++ {
        y := float64(py) / height * (ymax - ymin) + ymin
        for px := 0; px < width; px++ {
            x := float64(px)/width*(xmax-xmin) + xmin
            z := complex(x, y)
            img.Set(px, py, f(z))
        }
    }
    png.Encode(w, img)
}

func maxsqr(x uint8) uint8 {
    if x > 16 {
        x = 16
    }
    return x*x
}

func Mandelbrot(z complex128) color.Color {
    const iterations = 200

    var v complex128
    for n := uint8(0); n < iterations; n++ {
        v = v*v + z
        if cmplx.Abs(v) > 2 {
            return color.RGBA{n / 2, n, maxsqr(n), 255}
        }
    }
    return color.Black
}

var basecolor = [...]color.YCbCr{color.YCbCr{109, 105, 203}, // English Vermillion
    color.YCbCr{219, 139, 99}, // Powder blue
    color.YCbCr{197, 54, 182}, // Yellow Orange
    color.YCbCr{220, 15, 127}, // Arctic Lime
    color.YCbCr{70, 172, 102}} // Dark Cornflower Blue
// Root colors will cycle through these five
// Problem: for 6, 11, etc. last color = first color

func thecolor(i int, iter uint8) color.Color {
    col := basecolor[i % len(basecolor)]
    col.Y = uint8(float64(col.Y) * math.Pow(.92, float64(iter)))
    return col
}

func Roots4(z complex128) color.Color {
    const iterations = 80
    roots := [...]complex128{1, 1i, -1, -1i}
    // cmplx.Exp(2i*k*Math.Pi / n) , k = 0 to n - 1

    for n := uint8(0); n < iterations; n++ {
        z = z - (z*z*z*z - 1)/(4*z*z*z)
        for i, root := range roots {
            if cmplx.Abs(z - root) < 0.002 {
                return thecolor(i, n)
            }
        }
    }
    return color.Black
}

func NewRootsUnity(n int) colorfunc {
    const iterations = 120
    coef := float64(n)
    roots := make([]complex128, 0, n)
    for k := 0; k < n; k++ {
        roots = append(roots, cmplx.Exp(complex(0, 2*float64(k)*math.Pi / coef)))
    }
    log.Printf("%dth roots: %v\n", n, roots)
    
    return func(z complex128) color.Color {
        for iter := uint8(0); iter < iterations; iter++ {
            zpow := cmplx.Pow(z, complex(coef-1, 0))
            z -= (zpow*z - 1)/complex(coef*real(zpow), coef*imag(zpow))
            for i, root := range roots {
                if cmplx.Abs(z - root) < thresh {
                    return thecolor(i, iter)
                }
            }
        }
        return color.Black
    }
}

type IPoly []int
// [a0, a1, a2, ..., a_n] represents a0 + a1*z + a2*z^2 + ... + z_n * z^n

func (coefs IPoly) apply(z complex128) complex128 {
    curpow := 1 + 0i
    sum := 0 + 0i
    for _, c := range coefs {
        rco := float64(c)
        sum += complex(rco * real(curpow), rco*imag(curpow))
        curpow *= z
    }
    return sum
}

func (coefs IPoly) differentiate() IPoly {
    newcoefs := make(IPoly, len(coefs) - 1)
    for i := 0; i < len(newcoefs); i++ {
        newcoefs[i] = (i+1) * coefs[i+1]
    }
    return newcoefs
}

func NewPolyFractal(coefs IPoly) colorfunc {
    const iterations = 200
    roots := make([]complex128, 0, len(coefs))
    df := coefs.differentiate()
    return func(z complex128) color.Color {
        for iter := uint8(0); iter < iterations; iter++ {
            newz := z - coefs.apply(z)/df.apply(z)
            dif := cmplx.Abs(newz - z)
            z = newz
            if dif < thresh {
                for i, root := range roots {
                    if cmplx.Abs(z - root) < thresh {
                        return thecolor(i, iter)
                    }
                }
                // no nearby root already in roots
                roots = append(roots, z)
                return thecolor(len(roots)-1, iter)
            }
        }
        return color.Black
    }
}
