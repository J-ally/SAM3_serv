import logging
from video.cropper import mask_to_bbox, write_cropped
from sam3.visualization_utils import prepare_masks_for_visualization

logger = logging.getLogger(__name__)


def run_extraction(
    sam,
    video_path: str,
    out_folder: str,
    prompt: str,
) -> None:
    """Run SAM-based object extraction and video cropping on a single video."""

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

        if not any(boxes.values()):
            continue

        write_cropped(
            video_path,
            out_folder,
            boxes,
            obj_id,
        )
