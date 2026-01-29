import subprocess
import os
import logging
import config
import re

# Paramètres du serveur SFTP
SFTP_USER = "sftpiodaa"
SFTP_HOST = "88.189.55.27"
SFTP_PORT = 22222
REMOTE_DIR = "/PACECOWVID/COPTIERE"
UPLOAD_DIR = "/PACECOWVID/ViTCow_upload"
LOCAL_TMP_DIR = "/home/kind_boyd/workdir/data"  # dossier local temporaire
FARM_NAME = "COPTIERE"


def list_sftp_videos():
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


def download_sftp_video(remote_path):
    filename = os.path.basename(remote_path)
    logging.info("Downloading video %s from %s", filename, REMOTE_DIR)
    local_path = os.path.join(LOCAL_TMP_DIR, filename)

    os.makedirs(LOCAL_TMP_DIR, exist_ok=True)

    cmd = f"echo 'get {remote_path} {local_path}' | sftp -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
    subprocess.run(cmd, shell=True, check=True)
    return local_path

def remove_video(local_path):
    """Supprime un fichier vidéo en vérifiant qu'il existe."""
    if os.path.exists(local_path):
        os.remove(local_path)

def mkdir_sftp(remote_dir):
    folders = remote_dir.strip("/").split("/")

    path = ""
    if remote_dir.startswith("/"):
        path = "/"

    for folder in folders:
        path = os.path.join(path, folder)

        # Vérifier si le dossier existe
        check_cmd = f"echo 'ls {path}\nexit' | sftp -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

        if "No such file" in result.stderr or "No such file" in result.stdout:
            mkdir_cmd = f"echo 'mkdir {path}\nexit' | sftp -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
            subprocess.run(mkdir_cmd, shell=True, check=True)
            logging.info("Dossier %s créé", path)
        else:
            # Dossier existe → ne rien faire, ne pas loguer
            pass

def upload_video(local_path, PREFIXE=FARM_NAME):
    "Télécharge la vidéo sur le cloud avec un préfixe dans le nom de fichier"
    original_filename = os.path.basename(local_path)
    
    filename = f"{PREFIXE}_{original_filename}"
    
    remote_dir_full = f"{UPLOAD_DIR}{REMOTE_DIR.removeprefix('/PACECOWVID')}"
    logging.info("Uploading video %s to %s", filename, remote_dir_full)
    
    mkdir_sftp(remote_dir_full)

    put_cmd = f"echo 'put {local_path} {remote_dir_full}/{filename}\nexit' | sftp -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
    subprocess.run(put_cmd, shell=True, check=True)

    return local_path
