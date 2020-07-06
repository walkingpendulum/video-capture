#! /usr/bin/env python
from __future__ import annotations

import argparse
import math
import subprocess
import time
import warnings
from typing import Type

import cv2
from tqdm import trange

from storages import BaseImageStorage, BufferedDiskStorage, DiskStorage

image_storage_classes = {
    "memory": BufferedDiskStorage,
}


def count_with_exact_fps(fps, duration_sec):
    total_iterations = int(fps * duration_sec)
    iter_target_duration_sec = 1.0 / fps
    eps = iter_target_duration_sec / 1.5
    delays = []
    for i in trange(total_iterations, desc="Capturing screenshots"):
        iter_start_time = time.time()
        yield i
        iter_lasted = time.time() - iter_start_time
        to_sleep_sec = iter_target_duration_sec - iter_lasted
        if to_sleep_sec > 0 and math.fabs(to_sleep_sec) > eps:
            time.sleep(iter_target_duration_sec - iter_lasted)
        elif to_sleep_sec < 0 and math.fabs(to_sleep_sec) > eps:
            delays.append({"iteration": i, "delay": iter_lasted - iter_target_duration_sec})

    if delays:
        delays_to_show = min(len(delays), 10)
        sorted_delays = sorted(delays, key=lambda r: r["delay"], reverse=True)
        formatted_delays = ", ".join([f"#{r['iteration']} by {r['delay']:.3}s" for r in sorted_delays[:delays_to_show]])
        msg = f"{len(delays)} out of {total_iterations} iterations completed with delays. " \
              f"Top {delays_to_show} are: {formatted_delays}"
        warnings.warn(msg, UserWarning)


def get_parser():
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--duration", help="Target video duration (in seconds)", default=10, type=float)
    parser.add_argument("--fps", help="Frames per second", default=30, type=float)
    parser.add_argument("--output", help="Target video path", default="video.mp4")
    parser.add_argument("--store-method", choices=["default", "memory"], default="default",
                        help="The method we will process captured images: dump to disk right after capturing (default) "
                             "or store in memory until the end and then dump all. Default method can be slower "
                             "for big fps, memory buffer is faster but requires more RAM "
                             "for big `fps * duration` values",
                        )

    return parser


def main(duration_sec, fps, target_video_path, storage_cls: Type[BaseImageStorage]):
    cap = cv2.VideoCapture(0)
    with storage_cls.store() as storage:
        storage: BaseImageStorage
        for _ in count_with_exact_fps(fps=fps, duration_sec=duration_sec):
            ret, frame = cap.read()
            storage.add_image(frame)

        cap.release()
        storage.flush_images()

        cmd = [
            "ffmpeg",
            "-y",  # overwrite
            "-hide_banner", "-loglevel", "panic",  # verbosity
            "-r", str(fps),
        ]
        cmd += storage.provide_ffmpeg_infile_options()
        cmd += [target_video_path]

        print("Call:", *cmd)
        subprocess.check_call(cmd)

    print("Done")


def cli(argv=None):
    args = get_parser().parse_args(argv)

    duration = args.duration
    fps = args.fps
    output = args.output
    store_method = args.store_method

    storage_class: Type[BaseImageStorage] = image_storage_classes.get(store_method, DiskStorage)

    main(
        duration_sec=duration,
        fps=fps,
        target_video_path=output,
        storage_cls=storage_class,
    )


if __name__ == '__main__':
    cli()
