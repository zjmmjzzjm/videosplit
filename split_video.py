import argparse
import subprocess
import json
import os
import math
import sys

def parse_size(size_str):
    """Parses a human-readable size string (e.g., '100MB', '2GB') into bytes."""
    size_str = size_str.strip().upper()
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    
    number = ""
    unit = ""
    
    for char in size_str:
        if char.isdigit() or char == '.':
            number += char
        else:
            unit += char
            
    unit = unit.strip()
    
    if not number:
        raise ValueError(f"Invalid size format: {size_str}")
        
    try:
        value = float(number)
    except ValueError:
        raise ValueError(f"Invalid number in size: {size_str}")
        
    if not unit:
        return int(value) # Assume bytes if no unit
        
    if unit in units:
        return int(value * units[unit])
    
    # Handle cases like "M" instead of "MB"
    if unit + "B" in units:
        return int(value * units[unit + "B"])
        
    raise ValueError(f"Unknown unit: {unit}")

def get_video_info(file_path):
    """Retrieves video duration and size using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,size",
        "-of", "json",
        file_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"]), int(data["format"]["size"])
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e.stderr}")
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing ffprobe output: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: ffprobe not found. Please ensure ffmpeg is installed.")
        sys.exit(1)

def split_video(input_file, chunk_size_str):
    """Splits the video into chunks of approximately chunk_size."""
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    try:
        target_chunk_size = parse_size(chunk_size_str)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Analyzing '{input_file}'...")
    duration, file_size = get_video_info(input_file)
    
    print(f"Total Duration: {duration:.2f}s")
    print(f"Total Size: {file_size / (1024**3):.2f} GB")
    print(f"Target Chunk Size: {target_chunk_size / (1024**2):.2f} MB")

    if file_size <= target_chunk_size:
        print("Video is already smaller than the target chunk size. No splitting needed.")
        return

    # Calculate segment duration based on target chunk size
    # We want chunks to be as close to target_chunk_size as possible (but not exceeding it too much).
    # Previous logic: segment_time = duration / math.ceil(file_size / target_chunk_size) -> Equal sized chunks
    # New logic: segment_time = duration * (target_chunk_size / file_size) -> Chunks of target size + remainder
    
    # Safety factor: Reduce target size slightly (e.g. 98%) to account for VBR spikes and keyframe alignment
    # preventing the chunk from accidentally exceeding the limit if the limit is strict.
    safe_target_size = target_chunk_size * 0.98
    segment_time = duration * (safe_target_size / file_size)
    
    # Estimate number of chunks for display
    num_chunks = math.ceil(duration / segment_time)
    
    print(f"Splitting into approximately {num_chunks} chunks.")
    print(f"Estimated segment duration: {segment_time:.2f}s")

    # Create output directory
    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_dir = os.path.join(os.path.dirname(input_file), f"{name}_parts")
    os.makedirs(output_dir, exist_ok=True)
    
    output_pattern = os.path.join(output_dir, f"{name}_part%03d{ext}")

    # ffmpeg command
    # -c copy: Copy streams (lossless)
    # -f segment: Use segment muxer
    # -segment_time: Target duration for each segment
    # -reset_timestamps 1: Reset timestamps for each segment (good for compatibility)
    
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",
        "-f", "segment",
        "-segment_time", str(segment_time),
        "-reset_timestamps", "1",
        output_pattern
    ]
    
    print(f"Running ffmpeg...")
    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccess! Video split into chunks in '{output_dir}'")
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please ensure ffmpeg is installed.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a video file into smaller chunks based on target size (lossless).")
    parser.add_argument("input_file", help="Path to the input video file")
    parser.add_argument("chunk_size", help="Target chunk size (e.g., '2GB', '500MB')")
    
    args = parser.parse_args()
    
    split_video(args.input_file, args.chunk_size)
