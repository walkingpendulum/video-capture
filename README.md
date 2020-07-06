# video_capture

This is an example of capturing video via opencv-python and ffmpeg.

### Dependencies
* python3
* ffmpeg (`brew install ffmpeg` for macos)
* opencv-python and tqdm (`pip install -r requirements.txt`)
 
### Usage 
```text
usage: capture.py [-h] [--duration DURATION] [--fps FPS] [--output OUTPUT]

optional arguments:
  -h, --help           show this help message and exit
  --duration DURATION  Target video duration (in seconds) (default: 10)
  --fps FPS            Frame rate per second (default: 30)
  --output OUTPUT      Target video path (default: video.mp4)
```
