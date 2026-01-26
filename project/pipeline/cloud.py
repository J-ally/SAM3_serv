import subprocess
import os
import logging
import config

# Paramètres du serveur SFTP
SFTP_USER = "sftpiodaa"
SFTP_HOST = "88.189.55.27"
SFTP_PORT = 22222
REMOTE_DIR = "/PACECOWVID/COPTIERE/D01/"
UPLOAD_DIR = "/PACECOWVID/ViTCow_upload"
LOCAL_TMP_DIR = "/tmp"  # dossier local temporaire
FARM_NAME = "COPTIERE"

def list_sftp_videos():
    """Liste tous les fichiers .mp4 dans tous les sous-dossiers de COPTIERE."""
    # Liste tous les sous-dossiers
    cmd = ["sftp", "-P", str(SFTP_PORT), f"{SFTP_USER}@{SFTP_HOST}"]
    proc = subprocess.run(
        cmd,
        input=f"ls {REMOTE_DIR}\nexit\n",
        capture_output=True,
        text=True,
        check=True
    )
    lines = proc.stdout.splitlines()
    
    # Filtrer uniquement les dossiers D01, D02, ...
    folders = [line.strip() for line in lines if line.strip().startswith("D")]

    all_videos = []
    for folder in folders:
        remote_folder = os.path.join(REMOTE_DIR, folder)
        # Lister les fichiers .mp4 dans chaque dossier
        proc_folder = subprocess.run(
            cmd,
            input=f"ls {remote_folder}\nexit\n",
            capture_output=True,
            text=True,
            check=True
        )
        folder_lines = proc_folder.stdout.splitlines()
        mp4_files = [os.path.join(remote_folder, f.strip()) for f in folder_lines if f.strip().endswith(".mp4")]
        all_videos.extend(mp4_files)

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
