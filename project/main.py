import os
import subprocess
import logging
import config
from video.clipper import extract_clips

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logging.info("Pipeline started")

# Découpe des clips
extract_clips(
    config.INPUT_FOLDER,
    config.CLIP_FOLDER,
    config.NUM_FRAMES_PER_CLIP,
    config.FRAME_STEP,
)

# Lancer 1 process par clip
for clip in sorted(os.listdir(config.CLIP_FOLDER)):
    if not clip.lower().endswith(".mp4"):
        continue

    clip_path = os.path.join(config.CLIP_FOLDER, clip)

    logging.info("Processing clip %s", clip_path)

    subprocess.run(
        [
            "python",
            "process_clip.py",
            clip_path,
        ],
        check=True,
    )

logging.info("Pipeline finished")