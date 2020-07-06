import os
import tempfile
from contextlib import contextmanager
from typing import List

import cv2
from tqdm import tqdm


class BaseImageStorage:
    @classmethod
    @contextmanager
    def store(cls):
        raise NotImplemented

    def add_image(self, frame) -> None:
        raise NotImplemented

    def flush_images(self) -> None:
        pass

    def provide_ffmpeg_infile_options(self) -> List[str]:
        raise NotImplemented


class DiskStorage(BaseImageStorage):
    def __init__(self, dir_path: str):
        self.images_stored: int = 0
        self.dir_path = dir_path
        self.screenshot_name_template = "screenshot_%010d.jpg"

    @classmethod
    @contextmanager
    def store(cls):
        with tempfile.TemporaryDirectory() as dir_path:
            storage = cls(dir_path=dir_path)
            yield storage

    def add_image(self, frame) -> None:
        self.images_stored += 1
        screenshot_name = self.screenshot_name_template % self.images_stored
        screenshot_path = os.path.join(self.dir_path, screenshot_name)
        cv2.imwrite(screenshot_path, frame)

    def provide_ffmpeg_infile_options(self) -> List[str]:
        return ["-i", os.path.join(self.dir_path, self.screenshot_name_template)]


class BufferedDiskStorage(DiskStorage):
    def __init__(self, *args, **kwargs):
        super(BufferedDiskStorage, self).__init__(*args, **kwargs)
        self.buffer = []

    def add_image(self, frame) -> None:
        self.images_stored += 1
        screenshot_name = self.screenshot_name_template % self.images_stored
        screenshot_path = os.path.join(self.dir_path, screenshot_name)
        self.buffer.append((screenshot_path, frame))

    def flush_images(self) -> None:
        for screenshot_path, frame in tqdm(self.buffer, desc="Flushing storage buffer"):
            cv2.imwrite(screenshot_path, frame)

    def provide_ffmpeg_infile_options(self) -> List[str]:
        return ["-i", os.path.join(self.dir_path, self.screenshot_name_template)]
