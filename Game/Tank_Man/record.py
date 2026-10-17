"""
Run a game with mlgame and save it as an mp4.

Takes the same arguments as `python -m mlgame`, e.g.
    python record.py -f 120 -i ml/ml_play.py -i ml/ml_play.py . --green_team_num 1 --blue_team_num 1 --frame_limit 1000

mlgame saves every frame as a jpg (-o), then this script turns the frames into
<out>/<timestamp>.mp4 and deletes the jpgs. Only one round is played (-1).
Put --out / --record_fps before the mlgame arguments to change them.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import imageio_ffmpeg

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("--out", default="recordings", help="The folder to save the mp4 into")
parser.add_argument("--record_fps", type=int, default=60, help="The fps of the recorded video")
args, mlgame_args = parser.parse_known_args()

os.makedirs(args.out, exist_ok=True)
frame_root = tempfile.mkdtemp(prefix="frames_", dir=args.out)
try:
    one_shot = [] if "-1" in mlgame_args or "--one-shot" in mlgame_args else ["-1"]
    subprocess.run([sys.executable, "-m", "mlgame", *one_shot, "-o", frame_root, *mlgame_args])

    # mlgame creates a timestamp folder inside the -o folder
    for frame_dir in sorted(glob.glob(os.path.join(frame_root, "*"))):
        if not glob.glob(os.path.join(frame_dir, "*.jpg")):
            continue
        video_path = os.path.join(args.out, f"{os.path.basename(frame_dir)}.mp4")
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                        "-framerate", str(args.record_fps), "-i", os.path.join(frame_dir, "%05d.jpg"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", video_path], check=True)
        print(f"Saved video: {video_path}")
finally:
    shutil.rmtree(frame_root, ignore_errors=True)
