import subprocess
import os
import logging

# Paramètres du serveur SFTP
SFTP_USER = "sftpiodaa"
SFTP_HOST = "88.189.55.27"
SFTP_PORT = 22222
REMOTE_DIR = "/PACECOWVID/COPTIERE/D01/"
LOCAL_TMP_DIR = "/tmp"  # dossier local temporaire

def list_sftp_videos():
    """Liste les fichiers .mp4 dans le dossier distant via SFTP."""
    cmd = ["sftp", "-P", str(SFTP_PORT), f"{SFTP_USER}@{SFTP_HOST}"]
    proc = subprocess.run(
        cmd, 
        input=f"ls {REMOTE_DIR}\nexit\n",
        capture_output=True, 
        text=True,
        check=True
    )
    lines = proc.stdout.splitlines()

    # Filtrer uniquement les lignes qui contiennent .mp4 et enlever les espaces
    mp4_files = [line.strip() for line in lines if line.strip().endswith(".mp4")]

    return mp4_files


def download_sftp_video(remote_path):
    filename = os.path.basename(remote_path)
    logging.info("Downloading video %s", filename)
    local_path = os.path.join(LOCAL_TMP_DIR, filename)

    os.makedirs(LOCAL_TMP_DIR, exist_ok=True)

    cmd = f"echo 'get {remote_path} {local_path}' | sftp -P {SFTP_PORT} {SFTP_USER}@{SFTP_HOST}"
    subprocess.run(cmd, shell=True, check=True)
    return local_path


def remove_local_video(local_path):
    """Supprime un fichier vidéo local temporaire."""
    if os.path.exists(local_path):
        os.remove(local_path)

# def upload_video(local_path):
#     "Télécharge la vidéo sur le cloud"
