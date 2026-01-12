import logging
from typing import Dict, List

import numpy as np
from transformers import Sam3VideoModel, Sam3VideoProcessor
import torch

logger = logging.getLogger(__name__)


class SAMSession:
    """Wrapper around SAM3 video predictor sessions."""

    def __init__(self) -> None:
        """Initialize the SAM3 video predictor."""
        logger.info("Initializing SAM3 predictor")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.predictor = Sam3VideoModel.from_pretrained("facebook/sam3").to(self.device).eval()
        self.processor = Sam3VideoProcessor.from_pretrained("facebook/sam3")
        

    def start(self, video_path: str):
        """Start a new SAM session for a video.

        Args:
            video_path: Path to the input video.
        Returns:
            An initialized streaming inference session object.
        """
        logger.info("Starting session for %s", video_path)
        streaming_inference_session = self.processor.init_video_session(
            inference_device=self.device,
            processing_device="cpu",
            video_storage_device="cpu",
         )
        return streaming_inference_session

    def add_prompt(
        self,
        inference_session: str,
        text: str,
    ):
        """Add a text prompt to a SAM session.

        Args:
            inference_session: Active streaming inference session.
            text: Text prompt describing the target object.

        Returns:
            The updated streaming inference session.
        """
        logger.info("Adding prompt '%s'", text)
        streaming_inference_session = self.processor.add_text_prompt(
            inference_session=inference_session,
            text=text,
        )
        return streaming_inference_session

    def propagate(self, 
                  streaming_inference_session,
                  batch_frames: List[np.ndarray],
                  start_frame_index: int,
                  batch_id: int,
        ) -> Dict[int, Dict[int, np.ndarray]]:
        """Propagate segmentation through the video.

        Args:
            streaming_inference_session: Initialized SAM3 streaming session
            with prompts already added.
            batch_frames: List of frames (H, W, C) in RGB format.
            start_frame_index: Global frame index offset for this batch.
            batch_id: Identifier of the current batch.

        Returns:
            Mapping from frame index to object masks.
        """
        logger.info("Propagating batch %s", batch_id)

        outputs: Dict[int, Dict[int, np.ndarray]] = {}

        for local_idx, frame in enumerate(batch_frames):
            # Preprocess single frame
            inputs = self.processor(
                images=frame,
                return_tensors="pt",
            )

            pixel_values = inputs.pixel_values.to(device=self.device)

            # Streaming inference (stateful)
            with torch.no_grad():
                model_outputs = self.predictor(
                    inference_session=streaming_inference_session,
                    frame=pixel_values[0],
                    reverse=False,
                )

            processed_outputs = self.processor.postprocess_outputs(
            streaming_inference_session,
            model_outputs,
            original_sizes=inputs.original_sizes,
            )

            global_frame_idx = start_frame_index + local_idx
            outputs[global_frame_idx] = processed_outputs

        logger.info(
            "Finished propagating frames %d to %d",
            start_frame_index,
            start_frame_index + len(batch_frames) - 1,
        )
        return outputs
