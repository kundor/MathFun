// Lissajous generates GIF animations of random Lissajous figures.
package lissajous

import (
	"fmt"
	"image"
	"image/color"
	"image/gif"
	"io"
	"log"
	"math"
	"math/rand"
	"os"
	"strconv"
	"time"
)

var palette = []color.Color{color.Black}

func init() {
	rand.Seed(time.Now().UTC().UnixNano())
	for r := uint8(0); r < 255; r += 5 {
		palette = append(palette, color.RGBA{r, 0, 255 - r, 255})
	}
}

var (
	cycles  = 5.0   // number of complete x oscillator revolutions
	res     = 0.002 // angular resolution
	size    = 200   // image canvas covers [-size..+size]
	nframes = 64
	delay   = 8   // delay between frames, centiseconds
	shift   = 0.1 // phase shift per frame
)

func ParseArgs(args []string) error {
	var err error
	if len(args) > 0 {
		cycles, err = strconv.ParseFloat(args[0], 64)
		if err != nil {
			return fmt.Errorf("First argument (number of oscillator revolutions) not convertible to float: %v", err)
		}
	}
	if len(args) > 1 {
		res, err = strconv.ParseFloat(args[1], 64)
		if err != nil {
			return fmt.Errorf("Second argument (angular resolution) not convertible to float: %v", err)
		}
	}
	if len(args) > 2 {
		size, err = strconv.Atoi(args[2])
		if err != nil {
			return fmt.Errorf("Third argument (canvas size) not convertible to int: %v", err)
		}
	}
	if len(args) > 3 {
		nframes, err = strconv.Atoi(args[3])
		if err != nil {
			return fmt.Errorf("Fourth argument (number of frames) not convertible to int: %v", err)
		}
	}
	if len(args) > 4 {
		delay, err = strconv.Atoi(args[4])
		if err != nil {
			return fmt.Errorf("Fifth argument (delay between frames in centiseconds) not convertible to int: %v", err)
		}
	}
	if len(args) > 5 {
		shift, err = strconv.ParseFloat(args[5], 64)
		if err != nil {
			return fmt.Errorf("Sixth argument (phase shift between frames) not convertible to float: %v", err)
		}
	}
	if len(args) > 6 {
		return fmt.Errorf("Too many arguments!")
	}
	return nil
}

func ParseMap(params map[string]string) {
	if val, found := params["cycles"]; found {
		cycles, _ = strconv.ParseFloat(val, 64)
	}
	if val, found := params["res"]; found {
		res, _ = strconv.ParseFloat(val, 64)
	}
	if val, found := params["size"]; found {
		size, _ = strconv.Atoi(val)
	}
	if val, found := params["nframes"]; found {
		nframes, _ = strconv.Atoi(val)
	}
	if val, found := params["delay"]; found {
		delay, _ = strconv.Atoi(val)
	}
	if val, found := params["shift"]; found {
		shift, _ = strconv.ParseFloat(val, 64)
	}
}

func Run() {
	err := ParseArgs(os.Args[1:])
	if err != nil {
		log.Fatal(err)
	}
	Lissajous(os.Stdout)
}

func Lissajous(out io.Writer) {
	freq := rand.Float64() * 3.0 // relative frequency of y oscillator
	anim := gif.GIF{LoopCount: nframes}
	phase := 0.0
	var colind uint8 = 1
	for i := 0; i < nframes; i++ {
		//        fmt.Fprintln(os.Stderr, len(palette))
		rect := image.Rect(0, 0, 2*size+1, 2*size+1)
		img := image.NewPaletted(rect, palette)
		for t := 0.0; t < cycles*2*math.Pi; t += res {
			x := math.Sin(t)
			y := math.Sin(t*freq + phase)
			img.SetColorIndex(size+int(x*float64(size)+0.5), size+int(y*float64(size)+0.5), colind)
			colind = uint8((t/(cycles*2*math.Pi))*float64(len(palette)) + 1.0)
		}
		phase += shift
		anim.Delay = append(anim.Delay, delay)
		anim.Image = append(anim.Image, img)
	}
	gif.EncodeAll(out, &anim)
}
