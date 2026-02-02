#!/bin/bash
# Test rapide du script de création d'issues
# Ce script vérifie que tout est prêt pour créer les issues

echo "🔍 Vérification de l'environnement..."
echo ""

# Vérifier Python
echo "1. Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Python installé: $PYTHON_VERSION"
else
    echo "   ❌ Python 3 n'est pas installé"
    echo "      Télécharger: https://www.python.org/downloads/"
    exit 1
fi

# Vérifier requests
echo ""
echo "2. Vérification du module requests..."
if python3 -c "import requests" 2>/dev/null; then
    REQUESTS_VERSION=$(python3 -c "import requests; print(requests.__version__)")
    echo "   ✅ Module requests installé: v$REQUESTS_VERSION"
else
    echo "   ⚠️  Module requests non installé"
    echo "      Installation: pip install requests"
    echo ""
    read -p "Voulez-vous l'installer maintenant? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install requests
        echo "   ✅ Module requests installé"
    else
        echo "   ❌ Installation annulée"
        exit 1
    fi
fi

# Vérifier le token
echo ""
echo "3. Vérification du token GitHub..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "   ⚠️  Variable GITHUB_TOKEN non définie"
    echo ""
    echo "   Options:"
    echo "   a) Définir maintenant: export GITHUB_TOKEN=your_token"
    echo "   b) Créer un fichier .env.issues"
    echo "   c) Passer le token au script: --token YOUR_TOKEN"
    echo ""
    echo "   Pour créer un token:"
    echo "   → GitHub → Settings → Developer settings"
    echo "   → Personal access tokens → Tokens (classic)"
    echo "   → Generate new token (classic)"
    echo "   → Sélectionner 'repo' scope"
    echo ""
else
    echo "   ✅ Token défini"
    
    # Tester le token
    echo "      Test de connexion à l'API GitHub..."
    RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
    
    if echo "$RESPONSE" | grep -q "login"; then
        USERNAME=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('login', 'unknown'))")
        echo "      ✅ Token valide - Connecté en tant que: $USERNAME"
    else
        echo "      ❌ Token invalide ou expiré"
        echo "      Créer un nouveau token sur GitHub"
        exit 1
    fi
fi

# Vérifier les fichiers
echo ""
echo "4. Vérification des fichiers..."
MISSING_FILES=0

if [ -f "create_github_issues.py" ]; then
    echo "   ✅ create_github_issues.py"
else
    echo "   ❌ create_github_issues.py manquant"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ -f "create_issues.sh" ]; then
    echo "   ✅ create_issues.sh"
else
    echo "   ❌ create_issues.sh manquant"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ -f "GITHUB_ISSUES.md" ]; then
    echo "   ✅ GITHUB_ISSUES.md"
else
    echo "   ❌ GITHUB_ISSUES.md manquant"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo "   ❌ Fichiers manquants: $MISSING_FILES"
    exit 1
fi

# Vérifier les permissions
echo ""
echo "5. Vérification des permissions..."
if [ -x "create_github_issues.py" ]; then
    echo "   ✅ create_github_issues.py exécutable"
else
    echo "   ⚠️  create_github_issues.py pas exécutable"
    chmod +x create_github_issues.py
    echo "      ✅ Permission ajoutée"
fi

if [ -x "create_issues.sh" ]; then
    echo "   ✅ create_issues.sh exécutable"
else
    echo "   ⚠️  create_issues.sh pas exécutable"
    chmod +x create_issues.sh
    echo "      ✅ Permission ajoutée"
fi

# Résumé
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ENVIRONNEMENT PRÊT !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Prochaines étapes:"
echo ""
echo "1. Tester sans créer (recommandé):"
echo "   ./create_issues.sh --dry-run"
echo ""
echo "2. Créer les issues:"
echo "   ./create_issues.sh --create"
echo ""
echo "3. Vérifier sur GitHub:"
echo "   https://github.com/donaldte/tech-articles/issues"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
