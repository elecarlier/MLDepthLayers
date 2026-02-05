#!/usr/bin/env bash
#
# Apple Depth Pro – téléchargement du checkpoint
#
# For licensing see accompanying LICENSE file.
# Copyright (C) 2024 Apple Inc.
#

set -e

CHECKPOINT_DIR="checkpoints"
CHECKPOINT_FILE="$CHECKPOINT_DIR/depth_pro.pt"
CHECKPOINT_URL="https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt"

# Crée le dossier checkpoints si nécessaire
mkdir -p "$CHECKPOINT_DIR"

# Si le checkpoint existe déjà, on sort
if [ -f "$CHECKPOINT_FILE" ]; then
    echo "✅ Checkpoint déjà présent : $CHECKPOINT_FILE"
    exit 0
fi

echo "📦 Checkpoint Depth Pro introuvable."

# Cas 1 : wget disponible
if command -v wget >/dev/null 2>&1; then
    echo "⬇️  Téléchargement avec wget…"
    wget "$CHECKPOINT_URL" -O "$CHECKPOINT_FILE"
    echo "✅ Téléchargement terminé."
    exit 0
fi

# Cas 2 : curl disponible
if command -v curl >/dev/null 2>&1; then
    echo "⬇️  Téléchargement avec curl…"
    curl -L "$CHECKPOINT_URL" -o "$CHECKPOINT_FILE"
    echo "✅ Téléchargement terminé."
    exit 0
fi

# Cas 3 : aucun outil disponible → instructions manuelles
echo "⚠️  Aucun outil de téléchargement automatique trouvé (wget / curl)."
echo
echo "👉 Téléchargement manuel requis :"
echo "1️⃣  Ouvre ce lien dans ton navigateur :"
echo "    $CHECKPOINT_URL"
echo "2️⃣  Télécharge le fichier depth_pro.pt"
echo "3️⃣  Place-le dans le dossier : $CHECKPOINT_DIR/"
echo
echo "Puis relance ton programme normalement."
exit 1
