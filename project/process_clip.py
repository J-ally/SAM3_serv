import sys
import os
import logging
import torch
import gc
import config
from pipeline.extractor import run_extraction
from sam.sam_session import SAMSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

def main():
    video_path = sys.argv[1]

    logging.info("Starting SAM worker for %s", video_path)

    sam = SAMSession()

    try:
        out_all_paths = run_extraction(
            sam,
            video_path,
            config.CROP_FOLDER,
            config.PROMPT_CLASS,
        )
    finally:
        del sam
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        gc.collect()

    logging.info("Finished %s", video_path)
    print(out_all_paths)

if __name__ == "__main__":
    main()
