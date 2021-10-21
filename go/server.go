// Server is a server for some mathematical image creators.
package main

import (
	"fmt"
	"log"
	"math"
	"net/http"
	"os/exec"
	"path"
	"strconv"
	"strings"
	"sync"

	"fractal"
	"lissajous"
	"surface"
)

var mu sync.Mutex
var counts map[string]int

const thresh = 0.000001 // for expressions fed to bc; clamp |x| >= thresh.
// This avoids dividing by zero (also in terms of r) which hangs the bc interaction.

func main() {
	counts = make(map[string]int)
	http.HandleFunc("/", index)
	http.Handle("/favicon.ico", http.NotFoundHandler())
	http.HandleFunc("/echo/", echoer)
	http.HandleFunc("/count", counter)
	http.HandleFunc("/lissajous/", lisser)
	http.HandleFunc("/surface/", surfer)
	http.HandleFunc("/mandelbrot/", mander)
	http.HandleFunc("/unity/", uniter)
	http.HandleFunc("/newton", newter)
	log.Fatal(http.ListenAndServe(":8000", nil))
}

func countme(name string, r *http.Request) {
	log.Printf("request for %q", r.URL.Path)
	mu.Lock()
	counts[name]++
	mu.Unlock()
}

func index(w http.ResponseWriter, r *http.Request) {
	countme("index", r)
	fmt.Fprintf(w, `<html>
    <head>
    <title>GO SERVER GO</title>
    </head>
    <body>
    <ul>
    <li><a href="/echo">echo</a></li>
    <li><a href="/count">count</a></li>
    <li><a href="/lissajous">lissajous</a>
    <form action="/lissajous/" method="POST">
    <ul>
    <li><label for="cycles">Number of oscillator revolutions:</label><input type="number" step="any" value=5 id="cycles" name="cycles"></li>
    <li><label for="res">Angular resolution:</label><input type="number" step="any" value=0.002 id="res" name="res"></li>
    <li><label for="size">Half canvas size (pixels):</label><input type="number" value=200 id="size" name="size"></li>
    <li><label for="nframes">Number of frames:</label><input type="number" value=64 id="nframes" name="nframes"></li>
    <li><label for="delay">Delay between frames (centiseconds):</label><input type="number" value=8 id="delay" name="delay"></li>
    <li><label for="shift">Phase shift per frame:</label><input type="number" step="any" value="0.1" id="shift" name="shift"></li>
    </ul>
    <input type="submit">
    </form></li>
    <li><a href="/surface">surface</a> / <a href="surface/eggbox">Eggbox</a> <a href="surface/moguls">Moguls</a> <a href="surface/saddle">Saddle</a>
    <form action="/surface">
    <label for="func">Function for surface:</label><input type="text" name="func" id="func"><input type="submit">
    </form>
    <p>Note: <a href="https://www.gnu.org/software/bc/manual/html_mono/bc.html">bc syntax</a>.
    x, y, r, t available (x + iy = r*e^it). s(x) = sin(x), l(x) = ln(x), etc.</p>
    <p>For non-integer exponents 2^x enter e(x*l(2)).</p></li>
    <li><a href="/mandelbrot">mandelbrot</a></li>
    <li><a href="/unity">unity</a> / <a href="unity/2">2</a>
                                     <a href="unity/3">3</a>
                                     <a href="unity/4">4</a>
                                     <a href="unity/5">5</a>
                                     <a href="unity/6">6</a>
                                     <a href="unity/7">7</a>...
    </li>
    <li><form action="newton">
    <label for="coefs">Integer polynomial coefficients:</label><input type="text" name="coefs" id="coefs">
    <input type="submit">
    </form>
    <p>Space-separated coefficients a0 a1 ... a_n representing a_0 + a1*z + ... + a_n*z^n.</p>
    <p>Try "-1 0 0 0 0 1" (fifth roots of unity) or "2 -2 0 1".</p>
    </li>
    </ul>
    </body>
    </html>`)
}

//echoer echoes HTTP request.
func echoer(w http.ResponseWriter, r *http.Request) {
	countme("echo", r)
	fmt.Fprintf(w, "Method %s, URL %s, Proto %s\n", r.Method, r.URL, r.Proto)
	fmt.Fprintf(w, "Host: %q\n", r.Host)
	fmt.Fprintf(w, "RemoteAddr: %q\n\n", r.RemoteAddr)
	for k, v := range r.Header {
		fmt.Fprintf(w, "Header[%q] = %q\n", k, v)
	}
	if err := r.ParseForm(); err != nil {
		log.Print(err)
	}
	fmt.Fprintln(w)
	for k, v := range r.Form {
		fmt.Fprintf(w, "Form[%q] = %q\n", k, v)
	}
}

//counter echoes the number of calls so far
func counter(w http.ResponseWriter, r *http.Request) {
	log.Printf("request for %q", r.URL.Path)
	tot := 0
	mu.Lock()
	counts["count"]++
	for name, ct := range counts {
		fmt.Fprintf(w, "%v: Count %d\n", name, ct)
		tot += ct
	}
	mu.Unlock()
	fmt.Fprintf(w, "Total: %d\n", tot)
}

//lisser sends an animated lissajous figure GIF
func lisser(w http.ResponseWriter, r *http.Request) {
	countme("lissajous", r)
	params := map[string]string{}
	for _, key := range [...]string{"cycles", "res", "size", "nframes", "delay", "shift"} {
		val := r.FormValue(key)
		if val != "" {
			params[key] = val
		}
	}
	log.Printf("method %q, values %v\n", r.Method, params)
	lissajous.ParseMap(params)
	lissajous.Lissajous(w)
}

func surfer(w http.ResponseWriter, r *http.Request) {
	countme("surface", r)
	w.Header().Set("Content-Type", "image/svg+xml")
	surfunc := surface.Sinrdr
	base := path.Base(r.URL.Path)
	query := r.FormValue("surf")
	if query == "" && base != "surface" {
		query = base
	}
	switch strings.ToLower(query) {
	default:
		// Still Sinrdr
	case "moguls":
		surfunc = surface.Moguls
	case "eggbox":
		surfunc = surface.Eggbox
	case "saddle":
		surfunc = surface.Saddle
	}
	expr := r.FormValue("func")
	if expr != "" {
		log.Printf("Requested func %s\n", expr)
		cmd := exec.Command("bc", "-ql")
		stdin, _ := cmd.StdinPipe()
		stdout, _ := cmd.StdoutPipe()
		cmd.Start()
		surfunc = func(x, y float64) (val float64) {
			if math.Abs(x) < thresh {
				if x < 0 {
					x = -thresh
				} else {
					x = thresh
				}
			}
			r := math.Hypot(x, y)
			t := math.Atan2(y, x)
			fmt.Fprintf(stdin, "x=%f;y=%f;r=%f;t=%f;%s\n", x, y, r, t, expr)
			fmt.Fscanln(stdout, &val)
			return
		}
		//defer cmd.Process.Kill()
		defer cmd.Wait()
		defer stdin.Close()
	}
	surface.WriteSVG(w, surfunc)
}

func mander(w http.ResponseWriter, r *http.Request) {
	countme("mandelbrot", r)
	fractal.WritePNG(w, fractal.Mandelbrot)
}

func uniter(w http.ResponseWriter, r *http.Request) {
	countme("unity", r)
	base := path.Base(r.URL.Path)
	fn := fractal.Roots4
	if base != "unity" {
		n, err := strconv.Atoi(base)
		if err != nil {
			msg := fmt.Sprintf("%q is not convertible to integer", base)
			http.Error(w, msg, 418)
			return
		}
		fn = fractal.NewRootsUnity(n)
	}
	fractal.WritePNG(w, fn)
}

func newter(w http.ResponseWriter, r *http.Request) {
	countme("newton", r)
	coefs := strings.Fields(r.FormValue("coefs"))
	poly := make(fractal.IPoly, len(coefs))
	var err error
	for i, coef := range coefs {
		poly[i], err = strconv.Atoi(coef)
		if err != nil {
			msg := fmt.Sprintf("%q is not convertible to integer", coef)
			http.Error(w, msg, 418)
			return
		}
	}
	fn := fractal.NewPolyFractal(poly)
	fractal.WritePNG(w, fn)
}
