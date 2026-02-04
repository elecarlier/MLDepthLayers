#!/usr/bin/env bash
#
# For licensing see accompanying LICENSE file.
# Copyright (C) 2024 Apple Inc. All Rights Reserved.
#


# Crée le dossier checkpoints si nécessaire
mkdir -p checkpoints

# Vérifie si le checkpoint existe déjà
CHECKPOINT_FILE="checkpoints/depth_pro.pt"

if [ -f "$CHECKPOINT_FILE" ]; then
    echo "✅ Le checkpoint existe déjà : $CHECKPOINT_FILE"
    exit 0
fi

# Message pour l'utilisateur
echo "⚠️  Le checkpoint Depth Pro n'est pas présent."
echo "1️⃣  Ouvre ce lien dans ton navigateur pour télécharger le modèle :"
echo "    https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt"
echo "2️⃣  Place le fichier téléchargé dans le dossier : checkpoints/"
echo "3️⃣  Ensuite, relance le script ou lance le programme Python comme d'habitude :"
