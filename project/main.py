import os
import subprocess
import logging
import config
from video.clipper import extract_clips, is_daytime_video
from pipeline.cloud import list_sftp_videos, download_sftp_video, remove_video, upload_video
import json

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

    local_path = download_sftp_video(video_path)

    extract_clips(
        local_path,
        config.CLIP_FOLDER,
        config.NUM_FRAMES_PER_CLIP,
        config.FRAME_STEP,
        config.NUM_CLIP
    )

    remove_video(local_path)

    for clip in sorted(os.listdir(config.CLIP_FOLDER)):
        if not clip.lower().endswith(".mp4"):
            continue

        clip_path = os.path.join(config.CLIP_FOLDER, clip)
        logging.info("Processing clip %s", clip_path)

        try:
            result = subprocess.run(
                ["python", "process_clip.py", clip_path],
                capture_output=True,
                text=True,
                check=True
            )

            # Prendre uniquement la dernière ligne du stdout pour le JSON
            json_line = result.stdout.strip().splitlines()[-1]
            out_all_paths = json.loads(json_line)

            logging.info("out_all_paths: %s", out_all_paths)
            for out_path in out_all_paths:
                upload_video(out_path)
                remove_video(out_path)

        except subprocess.CalledProcessError as e:
            logging.error("Clip processing failed: %s", clip_path)
            logging.error("STDOUT: %s", e.stdout)
            logging.error("STDERR: %s", e.stderr)
            continue  # passe au clip suivant

        finally:
            # toujours supprimer le clip même si erreur
            remove_video(clip_path)

    logging.info("Finished video %s", os.path.basename(local_path))

logging.info("Pipeline finished")
