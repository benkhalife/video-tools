import os
import subprocess
import argparse


def generate_dash(input_file, output_dir="output_dash", resolutions=None, bitrates=None,
                  video_codec="libx264", audio_codec="aac", audio_bitrate="128k",
                  preset="slow", profile="main", gop=48, crf_values=None):
    """
    Convert MP4 to MPEG-DASH with multiple resolutions.
    If no bitrates are provided, CRF mode will be used (quality-based encoding).
    """

    if resolutions is None:
        resolutions = ["1920x1080", "1280x720", "854x480", "640x360"]

    # اگر بیت‌ریت داده نشده باشه → CRF استفاده میشه
    use_crf = bitrates is None

    if not use_crf and len(resolutions) != len(bitrates):
        raise ValueError("Number of resolutions and bitrates must match!")

    if use_crf:
        # مقادیر CRF هوشمند بر اساس رزولوشن
        # هرچه رزولوشن بالاتر → CRF کمتر (کیفیت بالاتر)
        default_crf = {
            "1920x1080": 22,
            "1280x720": 23,
            "854x480": 25,
            "640x360": 28
        }
        crf_values = [default_crf.get(r, 24) for r in resolutions]

    os.makedirs(output_dir, exist_ok=True)

    # scale filter
    filter_complex = ";".join([f"[0:v]scale={res}[v{i}]" for i, res in enumerate(resolutions)])
    cmd = [
        "/home/nitro/Downloads/Apps/Editing/ffmpeg-master/bin/ffmpeg", "-y",
        "-i", input_file,
        "-filter_complex", filter_complex
    ]

    for i, res in enumerate(resolutions):
        cmd += ["-map", f"[v{i}]",
                "-c:v", video_codec,
                "-preset", preset,
                "-profile:v", profile,
                "-keyint_min", str(gop),
                "-g", str(gop),
                "-sc_threshold", "0"]

        if use_crf:
            cmd += ["-crf", str(crf_values[i])]
        else:
            cmd += ["-b:v", bitrates[i]]

        # صدا
        cmd += ["-map", "0:a:0",
                "-c:a", audio_codec,
                "-b:a", audio_bitrate]

    cmd += [
        "-f", "dash",
        "-use_template", "1",
        "-use_timeline", "1",
        "-adaptation_sets", "id=0,streams=v id=1,streams=a",
        os.path.join(output_dir, "manifest.mpd")
    ]

    print("Running command:\n", " ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MP4 to MPEG-DASH with multiple resolutions.")
    parser.add_argument("input", help="Path to input MP4 file")
    parser.add_argument("-o", "--output", default="dash_output", help="Output directory")
    parser.add_argument("-r", "--resolutions", nargs="+",
                        default=["1920x1080", "1280x720", "854x480", "640x360"],
                        help="List of resolutions (e.g. 1920x1080 1280x720)")
    parser.add_argument("-b", "--bitrates", nargs="+",
                        help="List of bitrates (if omitted, CRF mode is used)")
    parser.add_argument("--vcodec", default="libx264", help="Video codec (default: libx264)")
    parser.add_argument("--acodec", default="aac", help="Audio codec (default: aac)")
    parser.add_argument("--abitrate", default="128k", help="Audio bitrate (default: 128k)")
    parser.add_argument("--preset", default="slow", help="FFmpeg preset (default: slow)")
    parser.add_argument("--profile", default="main", help="H264 profile (default: main)")
    parser.add_argument("--gop", type=int, default=48, help="Keyframe interval (default: 48)")

    args = parser.parse_args()

    generate_dash(
        input_file=args.input,
        output_dir=args.output,
        resolutions=args.resolutions,
        bitrates=args.bitrates,
        video_codec=args.vcodec,
        audio_codec=args.acodec,
        audio_bitrate=args.abitrate,
        preset=args.preset,
        profile=args.profile,
        gop=args.gop
    )
