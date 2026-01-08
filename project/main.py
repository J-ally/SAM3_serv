import logging
import os
import config
from video.clipper import extract_clips
from pipeline.extractor import run_extraction
from sam.sam_session import SAMSession
import torch
import gc

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logging.info("Pipeline started")

extract_clips(
    config.INPUT_FOLDER,
    config.CLIP_FOLDER,
    config.NUM_FRAMES_PER_CLIP,
    config.FRAME_STEP,
)

for clip in os.listdir(config.CLIP_FOLDER):
    sam = SAMSession()          # nouveau predictor
    try:
        if not clip.lower().endswith(".mp4"):
            continue

        video_path = os.path.join(config.CLIP_FOLDER, clip)

        run_extraction(
            sam,
            video_path,
            config.CROP_FOLDER,
            config.PROMPT_CLASS,
            config.PADDING,
        )
    finally:
        del sam
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        gc.collect()
logging.info("Pipeline finished")
