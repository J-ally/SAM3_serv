import cv2
import os
import logging
from tqdm import tqdm
import random

logger = logging.getLogger(__name__)

def is_daytime_video(filepath):
    """
    Vérifie si la vidéo se situe dans la tranche "jour" (06h00 - 18h00)
    d'après les 4 chiffres correspondant à l'heure dans le nom du fichier.
    Fonctionne avec un chemin complet ou juste le nom du fichier.
    Exemple de nom : 202502052200_D01.mp4
    """
    filename = os.path.basename(filepath) 
    try:
        hour_str = filename[8:12] 
        hour = int(hour_str[:2])
        return 9 <= hour < 17
    
    except Exception as e:
        logging.warning("Impossible de déterminer l'heure pour %s : %s", filename, e)
        return False


logger = logging.getLogger(__name__)

def extract_clips(
    video_path: str,
    output_folder: str,
    num_frames: int,
    step: int,
    num_clips: int
) -> None:
    """Extract a fixed number of clips randomly from a video.

    Args:
        video_path: Path to the input video.
        output_folder: Directory where output clips will be written.
        num_frames: Number of frames per output clip.
        step: Frame sampling step.
        num_clips: Number of clips to extract randomly.
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

    max_start_idx = total_frames - num_frames * step
    if max_start_idx <= 0:
        logger.warning("Video %s too short for clip extraction", name)
        return

    # Choisir aléatoirement les indices de départ pour les clips
    start_indices = random.sample(range(max_start_idx), min(num_clips, max_start_idx))

    pbar = tqdm(total=len(start_indices), desc=f"Clipping {name}", unit="clip")

    for clip_id, start_idx in enumerate(start_indices):
        frames = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
        for _ in range(num_frames * step):
            ret, frame = cap.read()
            if not ret:
                break
            # Échantillonnage selon step
            if len(frames) < num_frames and (_ % step == 0):
                frames.append(frame)

        if frames:
            out_path = os.path.join(output_folder, f"{name[:-4]}_clip{clip_id}_start{start_idx}.mp4")

            out = cv2.VideoWriter(
                out_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps / step,
                (w, h)
            )
            for f in frames:
                out.write(f)
            out.release()
        pbar.update(1)

    pbar.close()
    cap.release()
