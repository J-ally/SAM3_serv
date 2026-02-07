import os
from config import NUM_FRAMES_PER_CLIP, PRETRAIN_DIR

def build_videomae_list(video_dir: str, out_file: str):
    video_dir = os.path.abspath(video_dir)
    video_names=os.listdir(video_dir)
    with open(out_file, "w") as f:
        for name in video_names:
            path = os.path.join(video_dir, name)
            n_frames = NUM_FRAMES_PER_CLIP
            f.write(f"{path} {n_frames}\n")

video_dir = f"{PRETRAIN_DIR}/COPTIERE"
out_file = f"{PRETRAIN_DIR}/train.csv"
build_videomae_list(video_dir="Vitcow_upload/COPTIERE", 
                    out_file="Vitcow_upload/train.csv")