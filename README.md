# 🐄 VitCow — Analyse vidéo des comportements bovins

## Description

Ce projet vise à développer une pipeline permettant de suivre et analyser automatiquement les comportements des vaches à partir de vidéos RGB et infrarouges.  
L’objectif est d’explorer l’usage de **foundation models** pour deux tâches clés :

1. **Segmentation & Tracking** des vaches (SAM2 / SAM3).
2. **Apprentissage auto-supervisé** des comportements via **VideoMAE v2**.

Le but final est de comparer cette approche à des méthodes plus classiques basées sur la détection (YOLO, Faster R-CNN, etc.) et d’évaluer :
- la qualité des représentations,
- la robustesse aux occlusions,
- la performance en few-shot / zero-shot.

## Contenu du projet (préliminaire)

- Préparation des vidéos (RGB + IR)
- Suivi des vaches avec SAM2/SAM3
- Génération de sous-vidéos centrées
- Pré-entraînement VideoMAE v2
- Premières expériences d’évaluation

Le projet est en phase de mise en place — le dépôt évoluera au fur et à mesure.
