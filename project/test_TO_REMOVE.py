import os
import cv2
import torch
import logging

from sam.sam_session import SAMSession
from video.batcher import extract_batches 
from video.clipper import extract_clips
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


VIDEO_PATH = "/teamspace/studios/this_studio/Clip_bis/test_vaches_clip0.mp4"
BATCH_SIZE = 10
TEXT_PROMPT = "cow"
MAX_BATCHES = 2  # test minimal


def main():
    sam = SAMSession()

    streaming_session = sam.start(
        video_path=VIDEO_PATH
    )

    streaming_session = sam.add_prompt(
        inference_session=streaming_session,
        text=TEXT_PROMPT,
    )

    all_outputs = {}
    frame_offset = 0

    for batch_idx, batch in enumerate(
        extract_batches(VIDEO_PATH, BATCH_SIZE)
    ):
        logger.info("Processing batch %d", batch_idx)

        batch_rgb = [
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            for frame in batch
        ]

        outputs = sam.propagate(
            streaming_inference_session=streaming_session,
            batch_frames=batch_rgb,
            start_frame_index=frame_offset,
            batch_id = batch_idx,
        )

        all_outputs.update(outputs)
        frame_offset += len(batch)

        if batch_idx + 1 >= MAX_BATCHES:
            break

    print("Number of frames processed:", len(all_outputs))
    first_key = sorted(all_outputs.keys())[0]
    print("Example frame index:", first_key)
    print("Output type:", type(all_outputs[first_key]))

    # 5. Optional: save one mask for sanity check
    sample_outputs = all_outputs[first_key]
    if isinstance(sample_outputs, dict):
        first_obj_id = list(sample_outputs.keys())[0]
        mask = sample_outputs[first_obj_id]

        cv2.imwrite(
            "debug_mask.png",
            (mask > 0).astype("uint8") * 255,
        )
        print("Saved debug_mask.png")


if __name__ == "__main__":
    #extract_clips(
    #config.INPUT_FOLDER,
    #config.CLIP_FOLDER,
    #config.NUM_FRAMES_PER_CLIP,
    #config.FRAME_STEP,
    #)
    main()
