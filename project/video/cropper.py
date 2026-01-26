import cv2
import numpy as np
import os
import logging
from typing import Dict, Tuple, Optional
import config

logger = logging.getLogger(__name__)


# ============================================================
# MASK => BBOX
# ============================================================

def mask_to_bbox(mask: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


# ============================================================
# BBOX UTILS
# ============================================================

def bbox_size(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
    x1, y1, x2, y2 = bbox
    return x2 - x1, y2 - y1


def make_square_bbox(bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    w, h = bbox_size(bbox)
    side = max(w, h)

    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    half = side // 2

    return (
        cx - half,
        cy - half,
        cx + half,
        cy + half,
    )


# ============================================================
# CORE CROP
# ============================================================

def crop_with_clamp(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
    out_size: int,
) -> np.ndarray:
    fh, fw, _ = frame.shape
    x1, y1, x2, y2 = bbox

    sx1 = max(0, x1)
    sy1 = max(0, y1)
    sx2 = min(fw, x2)
    sy2 = min(fh, y2)

    crop = frame[sy1:sy2, sx1:sx2]

    out = np.zeros((out_size, out_size, 3), dtype=np.uint8)
    ox = sx1 - x1
    oy = sy1 - y1

    out[oy:oy + crop.shape[0], ox:ox + crop.shape[1]] = crop
    return out


# ============================================================
# PER-FRAME LOGIC
# ============================================================

def crop_frame(
    frame: np.ndarray,
    bbox: Optional[Tuple[int, int, int, int]],
) -> np.ndarray:

    if bbox is None:
        return np.zeros((config.CROP_SIZE, config.CROP_SIZE, 3), dtype=np.uint8)

    w, h = bbox_size(bbox)

    if max(w, h) > config.CROP_SIZE:
        square_bbox = make_square_bbox(bbox)
        side = max(w, h)

        square_crop = crop_with_clamp(
            frame,
            square_bbox,
            side,
        )

        return cv2.resize(
            square_crop,
            (config.CROP_SIZE, config.CROP_SIZE),
            interpolation=cv2.INTER_LINEAR,
        )

    return crop_with_clamp(
        frame,
        bbox,
        config.CROP_SIZE,
    )


# ============================================================
# VIDEO WRITER
# ============================================================

def write_cropped(
    video_path: str,
    out_folder: str,
    bboxes: Dict[int, Optional[Tuple[int, int, int, int]]],
    obj_id: int,
) -> None:

    os.makedirs(out_folder, exist_ok=True)
    logger.info("Writing cropped video for object %s", obj_id)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    # Trouver la première bbox non-None
    first_frame_idx = next((idx for idx, bb in bboxes.items() if bb is not None), None)
    if first_frame_idx is not None:
        first_bbox = bboxes[first_frame_idx]
        # Format: x1-y1-x2-y2
        bbox_str = "_".join(map(str, first_bbox))
    else:
        bbox_str = "no_bbox"

    # Créer le nom de fichier avec bbox
    name = os.path.basename(video_path).replace(".mp4", f"_{bbox_str}.mp4")

    out_path = os.path.join(out_folder, name)

    out = cv2.VideoWriter(
        os.path.join(out_folder, name),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (config.CROP_SIZE, config.CROP_SIZE),
    )

    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out.write(crop_frame(frame, bboxes.get(i)))
        i += 1

    cap.release()
    out.release()
    return out_path
