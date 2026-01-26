import cv2
import os
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


def extract_clips(
    video_path: str,
    output_folder: str,
    num_frames: int,
    step: int
) -> None:
    """Extract fixed-length clips from videos.

    Videos in the input directory are split into multiple clips by
    sampling one frame every `step` frames and grouping them into
    sequences of length `num_frames`.

    Args:
        video_path: Path to the input video.
        output_folder: Directory where output clips will be written.
        num_frames: Number of frames per output clip.
        step: Frame sampling step.
    """
    os.makedirs(output_folder, exist_ok=True)
    name = os.path.basename(video_path)

    logger.info("Clipping video %s", name)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        logger.warning("Could not open video %s", name)
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Nombre total de clips qu'on pourra générer
    total_clips = (total_frames // step) // num_frames

    frames = []
    frame_idx = 0
    clip_id = 0

    # Barre de progression
    pbar = tqdm(total=total_clips, desc=f"Clipping {name}", unit="clip")

    while True:
        #Si on veut faire des tests
        #if not clip_id < 5:
            #break
        
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            frames.append(frame)

        if len(frames) == num_frames:
            out_path = os.path.join(
                output_folder, f"{name[:-4]}_clip{clip_id}.mp4"
            )
            out = cv2.VideoWriter(
                out_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps / step,
                (w, h),
            )
            for f in frames:
                out.write(f)
            out.release()

            frames.clear()
            clip_id += 1
            pbar.update(1)

        frame_idx += 1
    pbar.close()
    cap.release()
