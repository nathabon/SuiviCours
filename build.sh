#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/var/www/suivicours"
VENV_DIR="$PROJECT_DIR/venv"
ENV_FILE="/etc/suivicours/suivicours.env"
BRANCH="main"
SERVICE_NAME="suivicours"

echo "=== Déploiement SuiviCours.fr ==="

cd "$PROJECT_DIR"

echo "1. Récupération du code depuis GitHub"
sudo -u ubuntu git fetch origin
sudo -u ubuntu git switch "$BRANCH"
sudo -u ubuntu git pull --ff-only origin "$BRANCH"

echo "2. Installation des dépendances"
sudo -u ubuntu "$VENV_DIR/bin/python" -m pip install \
    -r "$PROJECT_DIR/requirements.txt"

echo "3. Vérification et migrations Django"
sudo -u ubuntu bash -c "
    set -Eeuo pipefail
    set -a
    source '$ENV_FILE'
    set +a
    cd '$PROJECT_DIR'

    '$VENV_DIR/bin/python' manage.py check
    '$VENV_DIR/bin/python' manage.py migrate --noinput
    '$VENV_DIR/bin/python' manage.py collectstatic --noinput
"

echo "4. Redémarrage de Gunicorn"
systemctl restart "$SERVICE_NAME"

echo "5. Vérification du service"
systemctl is-active --quiet "$SERVICE_NAME"

echo "6. Vérification du site"
curl --fail --silent --show-error \
    --head https://suivicours.fr/ > /dev/null

echo "=== Déploiement terminé avec succès ==="