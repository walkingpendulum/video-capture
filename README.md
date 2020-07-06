# video_capture

This is an example of capturing video via opencv-python and ffmpeg.

### Dependencies
* python3
* ffmpeg (`brew install ffmpeg` for macos)
* opencv-python and tqdm (`pip install -r requirements.txt`)
 
### Usage 
```text
usage: capture.py [-h] [--duration DURATION] [--ifps IFPS] [--ofps OFPS] [--output OUTPUT] [--store-method {default,memory}]

optional arguments:
  -h, --help            show this help message and exit
  --duration DURATION   Target video duration (in seconds) (default: 10)
  --ifps IFPS           Frames per second for capturing (default: 30)
  --ofps OFPS           Frames per second for output video (default: None)
  --output OUTPUT       Target video path (default: video.mp4)
  --store-method {default,memory}
                        The method we will process captured images: dump to disk right after capturing (default) or store in memory until the end and then dump all. Default method can be slower
                        for big fps, memory buffer is faster but requires more RAM for big `fps * duration` values (default: default)
```
