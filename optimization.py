import subprocess
import os
import sys

def get_video_info(input_file):
    """Get original video file size"""
    size_bytes = os.path.getsize(input_file)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

def compress_video(input_file, output_file, crf=23, preset='slow'):
    """
    Compress video using H.264 codec with CRF encoding
    
    Args:
        input_file: Path to input MP4 file
        output_file: Path to output MP4 file
        crf: Constant Rate Factor (18-28 recommended, lower=better quality)
             23 is default, 18 is visually lossless
        preset: Encoding speed (ultrafast, superfast, veryfast, faster, 
                fast, medium, slow, slower, veryslow)
                Slower presets = better compression
    """
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return False
    
    # Get original size
    original_size = get_video_info(input_file)
    print(f"Original size: {original_size:.2f} MB")
    print(f"Compressing with CRF={crf}, preset={preset}...")
    
    # FFmpeg command for high-quality compression
    # -c:v libx264: Use H.264 codec
    # -crf: Constant Rate Factor (quality-based encoding)
    # -preset: Encoding speed/compression efficiency
    # -c:a copy: Copy audio without re-encoding (preserves quality)
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-preset', preset,
        '-c:a', 'copy',  # Copy audio stream as-is
        '-y',  # Overwrite output file if exists
        output_file
    ]
    
    try:
        # Run FFmpeg
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            compressed_size = get_video_info(output_file)
            reduction = ((original_size - compressed_size) / original_size) * 100
            
            print(f"\n✓ Compression successful!")
            print(f"Compressed size: {compressed_size:.2f} MB")
            print(f"Size reduction: {reduction:.1f}%")
            return True
        else:
            print(f"\n✗ Error during compression:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg first.")
        print("Visit: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    # Example usage
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'compressed_output.mp4'
    else:
        # Default example
        input_file = 'input_video.mp4'
        output_file = 'compressed_video.mp4'
    
    # CRF values guide:
    # 18 = visually lossless (high quality, larger file)
    # 23 = default (good quality, balanced)
    # 28 = acceptable quality (smaller file)
    
    compress_video(input_file, output_file, crf=23, preset='slow')

if __name__ == '__main__':
    main()