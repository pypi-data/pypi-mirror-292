#!/usr/bin/env python3

import argparse
import os
from argparse import Namespace
from pathlib import Path

from create_omp_audio_metrics import generate_audio_metrics
from create_omp_audio_waveforms import generate_audio_waveform
from create_omp_thumbnails import generate_thumbnail_track
from create_omp_video_bitrate import generate_video_bitrate_vtt


def create_audio_metrics(args: Namespace):
    """
    create_omp_tracks.py --audio-metrics [-i <input_file> | -o <input_dir>] -o <output_dir>
    """
    if args.verbose:
        input_info = args.input_file if args.input_file else args.input_dir
        print(f"Creating audio metrics: Input {input_info} | Output Directory: {args.output_dir}")

    if args.input_file:
        generate_audio_metrics(args.input_file, args.output_dir)
    else:
        for entry in os.scandir(args.input_dir):
            if entry.name.endswith('.wav') | entry.name.endswith('.aac'):
                generate_audio_metrics(entry.path, args.output_dir)


def create_waveforms(args: Namespace):
    """
    create_waveforms.py --waveforms [-i <input_file> | -o <input_dir>] -o <output_dir>
    """
    if args.verbose:
        input_info = args.input_file if args.input_file else args.input_dir
        print(f"Creating audio waveforms: Input {input_info} | Output Directory: {args.output_dir}")

    if args.input_file:
        generate_audio_waveform(args.input_file, args.output_dir, 1)
    else:
        for entry in os.scandir(args.input_dir):
            if entry.name.endswith('.wav') | entry.name.endswith('.aac'):
                generate_audio_waveform(entry.path, args.output_dir, 1)


def create_thumbnails(args: Namespace):
    """
    create_omp_tracks.py -thumbnails -i <input_file> -o <output_dir> -s <seconds_interval>
    """
    if args.input_dir:
        print("Input directory not supported for thumbnail track creation.")
        return
    elif Path(args.input_file).exists() is False:
        print(f"Input file {args.input_file} does not exist.")
        return

    if args.verbose:
        input_info = args.input_file if args.input_file else args.input_dir
        print(
            f"Creating thumbnails: Input {input_info} | Output Directory: {args.output_dir} | Seconds per Thumbnail: {args.seconds_interval}")

    generate_thumbnail_track(args.input_file, args.output_dir, args.seconds_interval)


def create_video_bitrate(args: Namespace):
    """
    create_omp_tracks.py --video-bitrate -i <input_file> -o <output_dir> -s <seconds_interval>
    """
    if args.input_dir:
        print("Input directory not supported for video bitrate track creation.")
        return
    elif Path(args.input_file).exists() is False:
        print(f"Input file {args.input_file} does not exist.")
        return

    if args.verbose:
        input_info = args.input_file if args.input_file else args.input_dir
        print(
            f"Creating video bitrate metrics: Input {input_info} | Output Directory: {args.output_dir} | Sample Interval: {args.seconds_interval}")

    if args.input_file:
        generate_video_bitrate_vtt(args.input_file, args.output_dir, args.seconds_interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create OMP metadata tracks.")
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")

    # Only one operation can be specified
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument("-w", "--waveforms", help="Create audio waveforms", action="store_true")
    operation_group.add_argument("-b", "--video-bitrate", help="Create video bitrate track", action="store_true")
    operation_group.add_argument("-a", "--audio-metrics", help="Create audio metrics track", action="store_true")
    operation_group.add_argument("-t", "--thumbnails", help="Create thumbnail track", action="store_true")

    # Make sure only a single file or an input directory is specified
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-i", "--input-file", help="Input file")
    input_group.add_argument("-d", "--input-dir", help="Input directory of files")

    parser.add_argument("-o", "--output-dir", help="Output directory", required=True)

    # Intervals over which generate thumbnails or video bitrate
    parser.add_argument(
        "-s", "--seconds-interval",
        help="Seconds between video bitrate samples or video thumbnails",
        default=2,
        choices=[1, 2, 3, 4, 5, 10, 12, 15],
        type=int)

    args = parser.parse_args()

    if args.waveforms:
        create_waveforms(args)

    elif args.video_bitrate:
        create_video_bitrate(args)

    elif args.audio_metrics:
        create_audio_metrics(args)

    elif args.thumbnails:
        create_thumbnails(args)
