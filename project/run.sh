#!/bin/bash

#git clone https://github.com/MariusCharles/PFR-ViTCow.git
#cd PFR-ViTCow/project/ || exit 1

pip install -r requirements.txt
git clone https://github.com/facebookresearch/sam3.git
pip install -e sam3

# -------------------------------
# Script pour modifier max_num_objects dans SAM3
# -------------------------------

# Chemin vers le fichier à modifier
FILE="/teamspace/studios/this_studio/PFR-ViTCow/project/sam3/sam3/model/sam3_video_base.py"

# Vérifie que le fichier existe
if [ ! -f "$FILE" ]; then
    echo "Erreur : fichier $FILE introuvable."
    exit 1
fi

# Remplace max_num_objects à la ligne 123 seulement
sed -i '123s/max_num_objects = 10000/max_num_objects = 5/' "$FILE"

# Vérifie si la modification a bien été faite
LINE_CONTENT=$(sed -n '123p' "$FILE")
echo "Contenu de la ligne 123 après modification : $LINE_CONTENT"

echo "Modification terminée"
