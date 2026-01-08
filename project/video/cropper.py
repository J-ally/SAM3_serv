import cv2
import numpy as np
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def mask_to_bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    """Convert a binary segmentation mask into a bounding box.

    The bounding box is computed as the minimal rectangle enclosing all
    non-zero pixels in the mask.

    Args:
        mask: Binary mask where non-zero values represent the object.

    Returns:
        Bounding box as (x_min, y_min, x_max, y_max), or None if the mask
        is empty.
    """
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def crop_black(
    frame: np.ndarray,
    bbox: tuple[int, int, int, int] | None,
    w: int,
    h: int,
) -> np.ndarray:
    """Crop a frame around a bounding box with black padding.

    If the bounding box exceeds the frame boundaries, missing areas
    are filled with black pixels. If the bounding box is None, a fully
    black frame is returned.

    Args:
        frame: Input video frame of shape (H, W, 3).
        bbox: Bounding box coordinates or None.
        w: Width of the output frame.
        h: Height of the output frame.

    Returns:
        Cropped frame of shape (h, w, 3).
    """
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    if bbox is None:
        return canvas

    fh, fw, _ = frame.shape
    x1, y1, x2, y2 = bbox
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

    sx = max(0, cx - w // 2)
    sy = max(0, cy - h // 2)
    ex = min(fw, sx + w)
    ey = min(fh, sy + h)

    crop = frame[sy:ey, sx:ex]
    ch, cw, _ = crop.shape
    ox, oy = (w - cw) // 2, (h - ch) // 2
    canvas[oy:oy + ch, ox:ox + cw] = crop

    return canvas


def write_cropped(
    video_path: str,
    out_folder: str,
    bboxes: Dict[int, tuple[int, int, int, int] | None],
    w: int,
    h: int,
    obj_id: int,
) -> None:
    """Write a cropped video based on per-frame bounding boxes.

    Each frame of the input video is cropped around the corresponding
    bounding box. If a bounding box is missing for a frame, a black
    frame is written instead.

    Args:
        video_path: Path to the input video file.
        out_folder: Directory where the cropped video will be saved.
        bboxes: Mapping from frame index to bounding box or None.
        w: Width of the output video.
        h: Height of the output video.
        obj_id: Identifier of the segmented object.

    Returns:
        None
    """
    os.makedirs(out_folder, exist_ok=True)
    logger.info("Writing cropped video for object %s", obj_id)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    name = os.path.basename(video_path).replace(".mp4", f"_{obj_id}.mp4")

    out = cv2.VideoWriter(
        os.path.join(out_folder, name),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h),
    )

    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(crop_black(frame, bboxes.get(i), w, h))
        i += 1

    cap.release()
    out.release()
