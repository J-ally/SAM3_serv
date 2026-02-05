import subprocess
import os
import logging
import config
import re

# Import SFTP server params 
from config import (
    SFTP_USER,
    SFTP_HOST,
    SFTP_PORT,
    REMOTE_DIR,
    UPLOAD_DIR,
    LOCAL_TMP_DIR, 
    FARM_NAME,
)


def list_sftp_videos() -> list:
    """Lists all video files from SFTP server folders.
    
    Returns:
        list: List of video filenames found on the SFTP server.
    """
    folder_pattern = re.compile(r"^D\d{2}$")
    video_pattern = re.compile(r"\.mp4$")

    cmd = ["sftp", "-P", str(SFTP_PORT), f"{SFTP_USER}@{SFTP_HOST}"]

    proc = subprocess.run(
        cmd,
        input=f"ls {REMOTE_DIR}\nexit\n",
        capture_output=True,
        text=True
    )

    folders = []
    for line in proc.stdout.splitlines():
        line = line.replace("sftp>", "").strip()
        if not line:
            continue

        name = os.path.basename(line)
        if folder_pattern.match(name):
            folders.append(name)

    all_videos = []

    for folder in folders:
        remote_folder = f"{REMOTE_DIR.rstrip('/')}/{folder}"

        proc_folder = subprocess.run(
            cmd,
            input=f"ls {remote_folder}\nexit\n",
            capture_output=True,
            text=True
        )

        for line in proc_folder.stdout.splitlines():
            line = line.replace("sftp>", "").strip()
            if not line:
                continue

            if video_pattern.search(line):
                all_videos.append(line)

    return all_videos


def download_sftp_video(remote_path: str) -> str:
    """Downloads a video file from the SFTP server.
    
    Args:
        remote_path (str): The remote path of the video file on the SFTP server.
    
    Returns:
        str: The local path where the video was downloaded.
    """
    filename = os.path.basename(remote_path)
    logging.info("Downloading video %s from %s", filename, REMOTE_DIR)
    local_path = os.path.join(LOCAL_TMP_DIR, filename)

    os.makedirs(LOCAL_TMP_DIR, exist_ok=True)

    cmd = f"echo 'get {remote_path} {local_path}' | sftp -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
    subprocess.run(cmd, shell=True, check=True)
    return local_path

def remove_video(local_path: str) -> None:
    """Removes a video file if it exists.
    
    Args:
        local_path (str): The local path of the video file to remove.
    """
    if os.path.exists(local_path):
        os.remove(local_path)


CREATED_FOLDERS = set()

def mkdir_sftp(remote_dir: str) -> None:
    if remote_dir in CREATED_FOLDERS:
        return
    
    folders = remote_dir.strip("/").split("/")
    cmds = []
    current_path = ""
    for folder in folders:
        current_path += f"/{folder}"
        cmds.append(f"-mkdir \"{current_path}\"")
    
    batch_cmds = "\n".join(cmds) + "\nexit"
    cmd = f"echo '{batch_cmds}' | sftp -b - -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        logging.info("Dossier %s prêt (créé ou existant) ", remote_dir)
        CREATED_FOLDERS.add(remote_dir)
    else:
        logging.error("Erreur de création du dossier %s (Code %d) : %s", 
                      remote_dir, result.returncode, result.stderr)
        


def upload_video(local_path: str, PREFIXE: str = FARM_NAME) -> str:
    """Uploads a video file to the SFTP server with a prefix in the filename.
    
    Args:
        local_path (str): The local path of the video file to upload.
        PREFIXE (str): The prefix to add to the filename. Defaults to FARM_NAME.
    
    Returns:
        str: The local path of the uploaded video.
    """
    original_filename = os.path.basename(local_path)
    
    filename = f"{PREFIXE}_{original_filename}"
    
    remote_dir_full = f"{UPLOAD_DIR}{REMOTE_DIR.removeprefix('/PACECOWVID')}"
    logging.info("Uploading video %s to %s", filename, remote_dir_full)
    
    mkdir_sftp(remote_dir_full)

    put_cmd = f"echo 'put {local_path} {remote_dir_full}/{filename}\nexit' | sftp -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
    subprocess.run(put_cmd, shell=True, check=True)

    return local_path


def check_if_exists(local_path: str) -> bool:
    """
    Vérifie récursivement si un fichier contenant local_path existe sur le serveur.
    
    Args:
        local_path (str): Le nom du clip à rechercher.
        
    Returns:
        bool: True si le fichier existe, False sinon.
    """
    find_cmd = (
        f"ssh -p {SFTP_PORT} {SFTP_USER}@{SFTP_HOST} "
        f"\"find {UPLOAD_DIR} -type f -name '*{local_path}*'\""
    )

    result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True)
    found_files = result.stdout.splitlines()

    pattern = re.compile(re.escape(local_path))  # échappe les caractères spéciaux

    try: 
        for f in found_files:
            basename = os.path.basename(f)
            if pattern.search(basename):
                logging.info(f"Fichier correspondant à '{local_path}' déjà présent sur le cloud : {f}")
                return True
        return False
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de la vérification sur le cloud : {e}")
        return False