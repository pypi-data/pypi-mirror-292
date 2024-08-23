# vclip

a small tool to compile randomly selected video clips from a folder of videos.

## example

for an example output of 100 randomly selected 1 second video clips see: https://vimeo.com/1001612646

## installation

vclip requires [moviepy](https://pypi.org/project/moviepy/).

to install vclip:

    pip install vclip

## usage

given a path to a folder of videos, vclip will output a video composed from 10 randomly selected 1 second clips using the following:

    vclip -i path/to/videos

## options

### help

    --help / -h

show help menu.

### input folder (-i / --input)

    --input [path] / -i [path]

path to folder of videos (default: current path).

### output file (-o / --output)

    --output [file name] / -o [file name]

name of output filename (default: timestamped file in format [year month day hour second] for when script is run - e.g. 20240818085410.mp4).

### number of clips (-n / --number)

    --number [number of clips] / -n [number of clips]

number of clips to compile from video folder (default: 10 clips).

### duration of clips (-d / --duration)

    --duration [duration of clips] / -d [duration of clips]

duration of clips to clip from videos in folder (default: 1 second).

### verbose (-v / --verbose)

    --verbose / -v

enable verbose output (logging).