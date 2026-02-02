#!/bin/bash
# Script simplifié pour créer les issues GitHub

set -e

echo "🚀 Création des Issues GitHub pour Tech Articles Platform"
echo "=========================================================="
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    echo "   Installez Python 3: https://www.python.org/downloads/"
    exit 1
fi

# Vérifier si requests est installé
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installation de la dépendance 'requests'..."
    pip3 install -r requirements-issues.txt
    echo "✅ Dépendance installée"
    echo ""
fi

# Vérifier si le token est défini
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  Variable GITHUB_TOKEN non définie"
    echo ""
    echo "Options:"
    echo "1. Définir la variable: export GITHUB_TOKEN=your_token"
    echo "2. Créer un fichier .env.issues (copier depuis .env.issues.example)"
    echo "3. Passer le token en argument: --token YOUR_TOKEN"
    echo ""
    
    # Charger depuis .env.issues si disponible
    if [ -f .env.issues ]; then
        echo "📄 Chargement depuis .env.issues..."
        export $(cat .env.issues | grep -v '^#' | xargs)
    else
        read -p "Voulez-vous entrer votre token maintenant? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -sp "Token GitHub: " GITHUB_TOKEN
            export GITHUB_TOKEN
            echo ""
        else
            echo "Annulé."
            exit 1
        fi
    fi
fi

# Repository par défaut
REPO="${GITHUB_REPO:-donaldte/tech-articles}"

# Mode dry-run par défaut pour sécurité
if [ "$1" == "--dry-run" ] || [ "$1" == "-d" ]; then
    echo "⚠️  MODE DRY-RUN: Aucune issue ne sera créée"
    echo ""
    python3 create_github_issues.py --repo "$REPO" --dry-run
elif [ "$1" == "--create" ] || [ "$1" == "-c" ]; then
    echo "✅ MODE CRÉATION: Les issues seront créées"
    echo ""
    read -p "Êtes-vous sûr de vouloir créer les issues? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 create_github_issues.py --repo "$REPO"
    else
        echo "Annulé."
        exit 0
    fi
else
    echo "Usage:"
    echo "  ./create_issues.sh --dry-run    # Tester sans créer"
    echo "  ./create_issues.sh --create     # Créer les issues"
    echo ""
    echo "Lancez d'abord en mode dry-run pour vérifier:"
    echo "  ./create_issues.sh --dry-run"
    exit 0
fi
