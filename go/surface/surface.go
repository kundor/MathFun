//Surface computes an SVG rendering of a 3-D surface function.
package surface

import (
	"fmt"
	"io"
	"math"
)

const (
	width, height = 800, 480            // canvas size in pixels
	cells         = 100                 // number of grid cells per side
	xyrange       = 30.0                // axis ranges (-xyrange..+xyrange)
	xyscale       = width / 2 / xyrange // pixels per x or y unit
	zscale        = height * 0.4        // pixels per z unit
	angle         = math.Pi / 6         // angle of x, y axes (30°)
)

var sin30, cos30 = math.Sin(angle), math.Cos(angle)

type surfunc func(float64, float64) float64

func WriteSVG(w io.Writer, f surfunc) {
	fmt.Fprintf(w, "<svg xmlns='http://www.w3.org/2000/svg' "+
		"style='stroke: grey; fill: white; stroke-width: 0.7' "+
		"width='%d' height='%d'>", width, height)
	for i := 0; i < cells; i++ {
		for j := 0; j < cells; j++ {
			ax, ay := corner(i+1, j, f)
			bx, by := corner(i, j, f)
			cx, cy := corner(i, j+1, f)
			dx, dy := corner(i+1, j+1, f)
			fmt.Fprintf(w, "<polygon points='%g,%g %g,%g %g,%g %g,%g'/>\n", ax, ay, bx, by, cx, cy, dx, dy)
		}
	}
	fmt.Fprintln(w, "</svg>")
}

func corner(i, j int, f surfunc) (float64, float64) {
	//Find point (x,y) at corner of cell (i,j).
	x := xyrange * (float64(i)/cells - 0.5) // note: dividing by a const 100 works, but by int 100 does not
	y := xyrange * (float64(j)/cells - 0.5)

	// Compute surface height z.
	z := f(x, y)

	//Project (x,y,z) isometrically onto 2-D SVG canvas (sx, sy).
	sx := width/2 + (x-y)*cos30*xyscale
	sy := height/2 + (x+y)*sin30*xyscale - z*zscale
	return sx, sy
}

func Sinrdr(x, y float64) float64 {
	r := math.Hypot(x, y)
	return math.Sin(r) / r
}

func Moguls(x, y float64) float64 {
	return math.Pow(2, math.Sin(x)) * math.Pow(2, math.Sin(y)) / 30
}

func Eggbox(x, y float64) float64 {
	return (math.Sin(x) * math.Sin(y)) / 10
}

func Saddle(x, y float64) float64 {
	return (x*x - y*y) / 240
}
