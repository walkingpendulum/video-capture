#! /usr/bin/env python
import argparse
import math
import os
import subprocess
import tempfile
import time
import warnings

import cv2
from tqdm import trange


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

    return parser


def main(duration_sec, fps, target_video_path):
    leading_zeroes_num = math.ceil(math.log10(duration_sec * fps))
    screenshot_name_template = f"screenshot_%0{leading_zeroes_num}d.jpg"

    cap = cv2.VideoCapture(0)
    with tempfile.TemporaryDirectory() as dir_path:
        g = count_with_exact_fps(fps=fps, duration_sec=duration_sec)
        for ind in g:
            ret, frame = cap.read()
            screenshot_name = screenshot_name_template % ind
            screenshot_path = os.path.join(dir_path, screenshot_name)
            cv2.imwrite(screenshot_path, frame)

        cap.release()
        cv2.destroyAllWindows()

        cmd = [
            "ffmpeg",
            "-y",  # overwrite
            "-hide_banner", "-loglevel", "panic",  # verbosity
            "-i", os.path.join(dir_path, screenshot_name_template),
            "-r", str(fps),
            target_video_path,
        ]
        print("Call:", *cmd)
        subprocess.check_call(cmd)

    print("Done")


def cli(argv=None):
    args = get_parser().parse_args(argv)

    duration = args.duration
    fps = args.fps
    output = args.output

    main(
        duration_sec=duration,
        fps=fps,
        target_video_path=output,
    )


if __name__ == '__main__':
    cli()
