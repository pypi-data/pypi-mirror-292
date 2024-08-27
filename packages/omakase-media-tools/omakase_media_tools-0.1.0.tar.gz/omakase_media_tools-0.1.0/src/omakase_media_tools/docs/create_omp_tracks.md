# create_omp_tracks.py

___

The Python script `create_omp_tracks.py` is used for creating Omakase Player temporal metadata tracks from source media
files. The script is capable of generating the following types of metadata tracks:

- **Audio Metric Analysis Tracks** using the `create_omp_tracks --audio-metrics` CLI option
- **Audio Waveform Analysis Tracks** using the `create_omp_tracks --waveforms` CLI option
- **Video Bitrate Analysis Tracks** using the `create_omp_tracks --video-bitrate` CLI option
- **Video Thumbnail Tracks** using the `create_omp_tracks --thumbnails` CLI option

Contents:

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Example Temporal Metadata Tracks](#example-temporal-metadata-tracks)
- [License](#license)

------

## Requirements

### Python

- Python 3.8 or higher

### ffmpeg

- Download a static build from the [ffmpeg website](http://ffmpeg.org/download.html) and install using the instructions
  for your platform.
- Ensure that the `ffmpeg` executable is in your path.

### audiowaveform

`audiowaveform` is a C++ program that takes an audio file and generates raw waveform data from it.

This data is then used to generate an OMP v1.0 VTT file containing the waveform metadata needed by the Omakase Player.

- download and install from GitHub here: [audiowaveform](https://github.com/bbc/audiowaveform)

### ffmpeg-bitrate-stats

The `ffmpeg-bitrate-stats` Python package is used to generate raw video bitrate metrics, when are then processed to
create a OMP v1.0 VTT file for use with Omakase Player.

- Install the `ffmpeg-bitrate-stats` Python package from the following GitHub
  repository: [ffmpeg-bitrate-stats](https://github.com/slhck/ffmpeg-bitrate-stats)

## Installation

- Clone the repository into your Python `venv`.
- Install the PIP package from PyPi.

## Usage

The Python script `create_omp_tracks.py` is a command line utility that can generate Omakase Player temporal metadata
tracks from source media files. It is capable of generating the following types of metadata tracks:

- **Audio Metric Analysis Tracks** using the `create_omp_tracks --audio-metrics` CLI option
- **Audio Waveform Analysis Tracks** using the `create_omp_tracks --waveforms` CLI option
- **Video Bitrate Analysis Tracks** using the `create_omp_tracks --video-bitrate` CLI option
- **Video Thumbnail Tracks** using the `create_omp_tracks --thumbnails` CLI option

## Usage create_omp_tracks.py --thumbnails

A thumbnail timeline metadata track and series of thumbnail images, can be generated with this option.

An input video file must be specified and the VTT and image files generated are written to the output directory
specified.

The frequency of the thumbnails is controlled by the `--seconds-interval` CLI option.

```text
usage: create_omp_tracks.py [-h] [-v] --thumbnails -i INPUT_FILE -o OUTPUT_DIR [-s {1,2,3,4,5,10,12,15}]

Create OMP thumbnail timeline metadata track.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output
  -t, --thumbnails      Create thumbnail track
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input file
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
  -s {1,2,3,4,5,10,12,15}, --seconds-interval {1,2,3,4,5,10,12,15}
                        Seconds between video bitrate samples or video thumbnails
```

### Example - Thumbnail Timeline Metadata Track

```text
WEBVTT

00:00:00.000 --> 00:00:01.999
tearsofsteel_4k00001.jpg

00:00:02.000 --> 00:00:03.999
tearsofsteel_4k00002.jpg
```

## Usage create_omp_tracks.py --video-bitrate

A metadata track of the video bitrate can be generated with this option. The resulting metadata track can then be used
to visualize the video bitrate as a line chart on the Omakase Player timeline.

```text
usage: create_omp_tracks.py [-h] [-v] --video-bitrate -i INPUT_FILE -o OUTPUT_DIR [-s {1,2,3,4,5,10,12,15}]

Create OMP video bitrate metadata track.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output
  -t, --video-bitrate   Create video bitrate track
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input file
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
  -s {1,2,3,4,5,10,12,15}, --seconds-interval {1,2,3,4,5,10,12,15}
                        Seconds between video bitrate samples or video thumbnails
```

An input video file must be specified and the VTT and image files generated are written to the output directory
specified.

The resolution of the bitrate samples is controlled by the `--seconds-interval` CLI option.

### Example - Video Bitrate Metadata Track

```text
WEBVTT

NOTE
Omakase Player Web VTT
V1.0

00:00:00.000 --> 00:00:01.999
276.39:MEASUREMENT=avg:COMMENT=2-sec interval
```

**Please Note:** The OMP v1.0 VTT file format is a standard WebVTT file with the following additional metadata:

- The `:MEASUREMENT=<metric name>` tag is optional and can be used to specify the video bitrate metric.
- The `:COMMENT=<comment>` tag is optional indicates the sample interval for the bitrate metric.

The optional tags are used by the Omakase Player to provide telemetry metadata for the video bitrate metric as the video
is played.

## Usage create_omp_tracks.py --audio-metrics

Audio metrics can be generated for an audio tracks, or all audio tracks, with this CLI option. At present, two audio
metric metadata tracks are created for each audio file:

- RMS Levels using the **ffmpeg** `ametadata` filter
- R128 Momentary Loudness also using the `ametadata` filter

If `--input-dir` is used, all of the `wav` and `aac` files in the current directory are processed. If `--input-file` is
used, only the audio file specified is processed.

The resulting metadata tracks are named with the basename of the audio file and appended with `R128_2-SEC` or
`RMS_2-SEC` respectively. All files are written to the directory specified with `--output-dir`.

At present, the metrics are calculated as an average over a two-second interval.

```text
usage: create_omp_tracks.py [-h] [-v] --audio-metrics (-i INPUT_FILE | -d INPUT_DIR) -o OUTPUT_DIR

Create OMP audio metric metadata tracks.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output
  -t, --video-bitrate   Create video bitrate track
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input file
  -d INPUT_DIR, --input-dir INPUT_DIR
                        Input directory of files
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
```

### Example - Audio Metrics Metadata Track

```text
WEBVTT

NOTE
Omakase Player Web VTT
V1.0

00:00:00.000 --> 00:00:01.999
-56.033:MEASUREMENT=lavfi.r128.M:COMMENT=2-sec avg
```

**Please Note:** The OMP v1.0 VTT file format is a standard WebVTT file with the following additional metadata:

- The `:MEASUREMENT=<metric name>` tag is optional and can be used to specify the audio metric type.
- The `:COMMENT=<comment>` tag is optional and can be used to provide additional information about the audio metric.

The optional tags are used by the Omakase Player to provide telemetry metadata for the audio metric as the video is
played.

## Usage create_omp_tracks.py --waveforms

The `--waveforms` option generates audio waveform metadata tracks that can be used to provide an audio waveform
visualization in Omakase Player.

Waveform metadata can be generated for a single audio track, or all audio tracks, with this CLI option. The
generated waveform includes the entire soundfield, but individual channels can be visualized with a dual-mono audio
track for each channel.

If `--input-dir` is used, all of the `wav` and `aac` files in the current directory are processed. If `--input-file` is
used, only the audio file specified is processed.

The resulting metadata tracks are named with the basename of the audio file All files are written to the directory
specified with `--output-dir`.

At present, the metrics are calculated as an average over a 1-second interval.

```text
usage: create_omp_tracks.py [-h] [-v] --waveforms (-i INPUT_FILE | -d INPUT_DIR) -o OUTPUT_DIR

Create OMP audio waveform metadata tracks.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output
  -t, --video-bitrate   Create video bitrate track
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input file
  -d INPUT_DIR, --input-dir INPUT_DIR
                        Input directory of files
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
```

### Example - Audio Waveform Metadata Track

```text
WEBVTT
  
00:00:00.000 --> 00:00:00.999
-0.0101, 0.0108
```

## License

`create_omp_tracks.py`, Copyright (c) 2024 Project Omakase LLC
