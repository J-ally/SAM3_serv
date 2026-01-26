import os
import subprocess
import logging
import config
import ast
from video.clipper import extract_clips, is_daytime_video
from pipeline.cloud import list_sftp_videos, download_sftp_video, remove_video, upload_video

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logging.info("Pipeline started")

videos_path = list_sftp_videos()

for video_path in videos_path:
    if not is_daytime_video(video_path):
        logging.info("Skipping night video %s", video_path)
        continue

    # Download the temporary video
    local_path = download_sftp_video(video_path)

    # Clip cutting
    extract_clips(
    local_path,
    config.CLIP_FOLDER,
    config.NUM_FRAMES_PER_CLIP,
    config.FRAME_STEP,
    config.NUM_CLIP
    )

    # Delete the temporary video
    remove_video(local_path)

    # Launch 1 process per clip
    for clip in sorted(os.listdir(config.CLIP_FOLDER)):
        if not clip.lower().endswith(".mp4"):
            continue

        clip_path = os.path.join(config.CLIP_FOLDER, clip)

        logging.info("Processing clip %s", clip_path)

        # result = subprocess.run(
        #     ["python", "process_clip.py", clip_path],
        #     capture_output=True,
        #     text=True,
        #     check=True
        # )
        
        # Delete the clip after processing
        remove_video(clip_path)

        # # Upload after processing
        # out_all_paths = ast.literal_eval(result.stdout.strip())
        # #A ENLEVER
        # logging.info("out_all_paths : %s", out_all_paths)
        # for out_path in out_all_paths:
        #     upload_video(out_path)

        # Deleting the crop after uploading
        remove_video(out_path)

    logging.info("Finished video %s", os.path.basename(local_path))

logging.info("Pipeline finished")
