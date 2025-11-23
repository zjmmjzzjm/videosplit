# Video Splitter

A simple Python script to split large video files into smaller chunks based on a target file size (e.g., "2GB", "500MB") while maintaining original quality (lossless).

## Features

- **Lossless Splitting**: Uses `ffmpeg` with `-c copy` to split videos without re-encoding, preserving original quality.
- **Size-Based Splitting**: You specify the maximum size for each chunk, and the script calculates the appropriate segment duration.
- **Fast**: Since it doesn't re-encode, the process is very fast (limited mostly by disk I/O).

## Prerequisites

- **Python 3**: Ensure Python 3 is installed.
- **FFmpeg**: The script relies on `ffmpeg` and `ffprobe`.
    - macOS: `brew install ffmpeg`
    - Ubuntu/Debian: `sudo apt install ffmpeg`
    - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Usage

Run the script from the terminal:

```bash
python3 split_video.py <input_file> <chunk_size>
```

### Arguments

- `input_path`: Path to the video file OR directory containing video files you want to split.
- `chunk_size`: The target maximum size for each chunk. Supports units like `MB`, `GB`.

### Examples

Split a single video into 2GB chunks:
```bash
python3 split_video.py my_large_video.mp4 2GB
```

Split all videos in a directory into 500MB chunks:
```bash
python3 split_video.py /path/to/videos 500MB
```

## Output

The script creates a directory named `<filename>_parts` in the same location as the input file. The split files will be named `<filename>_part000.ext`, `<filename>_part001.ext`, etc.

## Notes

- The splitting happens at keyframes, so the actual file size might be slightly larger or smaller than the target size. If your video has sparse keyframes (e.g., one every 10 seconds), the chunks might be larger than requested because `ffmpeg` cannot split between keyframes in copy mode.
- The script assumes a constant bitrate for size estimation, which is usually sufficient for splitting purposes.
