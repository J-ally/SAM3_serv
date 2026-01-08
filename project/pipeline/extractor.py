import logging
from video.cropper import mask_to_bbox, write_cropped
from sam3.visualization_utils import prepare_masks_for_visualization
import torch
import gc

logger = logging.getLogger(__name__)


def run_extraction(
    sam,
    video_path: str,
    out_folder: str,
    prompt: str,
    padding: int,
) -> None:
    """Run SAM-based object extraction and video cropping on a single video.

    This function executes a full segmentation and cropping pipeline using a
    preloaded SAM session:

    - Starts a SAM video session for the given video
    - Adds a text prompt on the first frame to initialize object segmentation
    - Propagates the segmentation through all frames of the video
    - Computes a bounding box per frame for each detected object
    - Determines a maximal bounding box size per object (with padding)
    - Writes a cropped output video for each detected object
    - Properly releases GPU and CPU resources at the end of the session

    Args:
        sam: An initialized SAMSession instance (model already loaded on GPU).
        video_path (str): Path to the input video file.
        out_folder (str): Directory where cropped videos will be saved.
        prompt (str): Text prompt used for SAM segmentation (e.g. object class).
        padding (int): Number of pixels added around the maximal bounding box.

    Returns:
        None

    Raises:
        RuntimeError: If the SAM session or inference fails internally.
    """
    sid = sam.start(video_path)
    first = sam.add_prompt(sid, prompt)
    outputs = sam.propagate(sid)

    outputs = prepare_masks_for_visualization(outputs)

    obj_ids = first.get("out_obj_ids", [])

    for obj_id in obj_ids:
        boxes = {}

        for idx, masks in outputs.items():
            if obj_id in masks:
                boxes[idx] = mask_to_bbox(masks[obj_id])
            else:
                boxes[idx] = None

        valid = [b for b in boxes.values() if b]
        if not valid:
            logger.warning(f"No valid bbox for object {obj_id}")
            continue

        max_w = max(b[2] - b[0] for b in valid) + 2 * padding
        max_h = max(b[3] - b[1] for b in valid) + 2 * padding

        write_cropped(
                video_path,
                out_folder,
                boxes,
                max_w,
                max_h,
                obj_id,
            )
