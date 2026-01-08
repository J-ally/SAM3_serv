import cv2
import os
import logging

logger = logging.getLogger(__name__)


def extract_clips(
    input_folder: str,
    output_folder: str,
    num_frames: int,
    step: int,
) -> None:
    """Extract fixed-length clips from videos.

    Videos in the input directory are split into multiple clips by
    sampling one frame every `step` frames and grouping them into
    sequences of length `num_frames`.

    Args:
        input_folder: Directory containing input video files.
        output_folder: Directory where output clips will be written.
        num_frames: Number of frames per output clip.
        step: Frame sampling step.
    """
    os.makedirs(output_folder, exist_ok=True)

    for name in os.listdir(input_folder):
        if not name.lower().endswith(".mp4"):
            continue

        logger.info("Clipping video %s", name)
        video_path = os.path.join(input_folder, name)
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.warning("Could not open video %s", name)
            continue

        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        frames = []
        frame_idx = 0
        clip_id = 0

        while True:
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

            frame_idx += 1

        cap.release()
