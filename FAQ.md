# ❓ FAQ - Questions Fréquentes

## 🚀 Démarrage

### Q: Par où commencer ?
**R:** Lisez [QUICK_START.txt](./QUICK_START.txt) - vous serez opérationnel en 5 minutes.

### Q: Dois-je tout lire ?
**R:** Non ! Voici le minimum :
1. QUICK_START.txt (2 min)
2. Créer un token GitHub (2 min)
3. Lancer le script (1 min)
C'est tout !

### Q: Quels fichiers sont vraiment nécessaires ?
**R:** Pour créer les issues automatiquement :
- `create_github_issues.py` ou `create_issues.sh`
- `requirements-issues.txt`
- Un token GitHub

Tout le reste est de la documentation optionnelle.

---

## 🔐 Token GitHub

### Q: Comment créer un token GitHub ?
**R:** 
1. GitHub.com → Votre avatar → Settings
2. Developer settings → Personal access tokens → Tokens (classic)
3. "Generate new token (classic)"
4. Nom : "Tech Articles Issues Creator"
5. Cocher : "repo" (full control of private repositories)
6. Generate token
7. **COPIER LE TOKEN** (vous ne le verrez qu'une fois!)

### Q: Quelle permission (scope) dois-je donner au token ?
**R:** Uniquement `repo` (full control of private repositories). C'est suffisant et c'est plus sûr.

### Q: Mon token est-il sécurisé ?
**R:** OUI, si vous suivez ces règles :
- ✅ Utilisez une variable d'environnement (`export GITHUB_TOKEN=...`)
- ✅ NE committez JAMAIS le token dans Git
- ✅ Révoquez le token après usage si nécessaire
- ✅ Le .gitignore protège .env.issues

### Q: Puis-je utiliser un token d'organisation ?
**R:** Oui, si vous avez les permissions nécessaires sur le repository.

### Q: Mon token expire-t-il ?
**R:** Les tokens "classic" n'expirent pas par défaut, mais vous pouvez définir une expiration pour plus de sécurité.

---

## 🛠️ Installation & Configuration

### Q: Quelles sont les dépendances ?
**R:** 
- Python 3.7+ (vérifié avec `python3 --version`)
- Package `requests` (installé avec `pip install requests`)
- Un token GitHub

### Q: Je n'ai pas Python, comment l'installer ?
**R:** 
- **Windows/Mac/Linux :** https://www.python.org/downloads/
- **Ubuntu/Debian :** `sudo apt install python3 python3-pip`
- **Mac (Homebrew) :** `brew install python3`

### Q: "Module requests not found" ?
**R:** 
```bash
pip install requests
# ou
pip3 install requests
# ou depuis le fichier
pip install -r requirements-issues.txt
```

### Q: Puis-je utiliser un environnement virtuel ?
**R:** Oui, recommandé !
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
pip install -r requirements-issues.txt
```

---

## 📝 Utilisation des Scripts

### Q: Quelle est la différence entre les scripts ?
**R:**
- **create_issues.sh** : Script bash simple, recommandé pour les débutants
- **create_github_issues.py** : Script Python direct, plus de contrôle
- **test_environment.sh** : Test de l'environnement avant création

### Q: Comment tester sans créer réellement ?
**R:** Utilisez le mode dry-run :
```bash
./create_issues.sh --dry-run
# ou
python3 create_github_issues.py --repo owner/repo --dry-run
```

### Q: Puis-je créer les issues sur un autre repository ?
**R:** Oui, changez le paramètre `--repo` :
```bash
python3 create_github_issues.py --repo other-owner/other-repo
```

### Q: Combien de temps prend la création ?
**R:** Environ 30-60 secondes pour créer :
- 25 labels
- 1 milestone
- 20 issues

### Q: Que fait exactement le script ?
**R:**
1. Crée 25 labels avec couleurs et descriptions
2. Crée le milestone "Launch v1.0" (échéance 22 fév)
3. Crée 20 issues avec :
   - Titre
   - Description complète
   - Labels appropriés
   - Liaison au milestone
4. Affiche un résumé

---

## ❌ Résolution de Problèmes

### Q: "Permission denied" sur les scripts ?
**R:** Rendez-les exécutables :
```bash
chmod +x create_issues.sh
chmod +x create_github_issues.py
chmod +x test_environment.sh
```

### Q: "Bad credentials" ou 401 error ?
**R:** Votre token est invalide. Vérifiez :
```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```
Si erreur, créez un nouveau token.

### Q: "Resource not accessible by integration" ?
**R:** Le token n'a pas le scope `repo`. Créez un nouveau token avec cette permission.

### Q: Les labels existent déjà ?
**R:** Pas de problème ! Le script détecte les labels existants et ne les recrée pas.

### Q: Le script se bloque ?
**R:** 
1. Vérifiez votre connexion internet
2. Vérifiez que l'API GitHub est accessible
3. Essayez en mode dry-run d'abord
4. Vérifiez les logs d'erreur

### Q: "Repository not found" ?
**R:** 
- Vérifiez le format : `owner/repo` (ex: `donaldte/tech-articles`)
- Vérifiez que vous avez accès au repository
- Vérifiez que le token a les bonnes permissions

---

## 📋 Issues & Planning

### Q: Pourquoi 20 issues exactement ?
**R:** C'est la décomposition complète des fonctionnalités demandées :
- 12 pour le dashboard admin
- 5 pour l'espace utilisateur
- Réparties logiquement sur 20 jours

### Q: Puis-je modifier les issues ?
**R:** Oui ! Les fichiers sont là pour vous aider, modifiez-les selon vos besoins :
- Éditez `create_github_issues.py` fonction `get_issues_data()`
- Ou créez les issues manuellement depuis GITHUB_ISSUES.md

### Q: Les échéances sont-elles fixes ?
**R:** Non, elles sont suggérées. Adaptez selon :
- La taille de votre équipe
- Vos disponibilités
- Vos priorités

### Q: Dois-je suivre l'ordre exact ?
**R:** Non, mais respectez les priorités :
- 🔴 Très Haute : À faire en premier (chemin critique)
- 🟠 Haute : Fonctionnalités essentielles
- 🟡 Moyenne : Amélioration UX
- 🟢 Basse : Nice-to-have

### Q: Puis-je travailler sur plusieurs issues en parallèle ?
**R:** Oui ! Le planning suggère 3 développeurs pour travailler en parallèle.

---

## 📁 Documentation

### Q: Quel fichier dois-je lire en premier ?
**R:** Selon votre profil :
- **Pressé ?** → QUICK_START.txt
- **Chef de projet ?** → ISSUES_SUMMARY.md puis PLANNING_GANTT.md
- **Développeur ?** → Attendez les issues sur GitHub
- **DevOps ?** → ISSUES_GUIDE.md

### Q: Pourquoi tant de fichiers de documentation ?
**R:** Pour s'adapter à tous les besoins :
- Guide rapide vs détaillé
- Texte brut vs Markdown
- Vue d'ensemble vs détails
- Planning vs technique

### Q: Puis-je supprimer certains fichiers ?
**R:** Après avoir créé les issues, vous pouvez garder seulement :
- GITHUB_ISSUES.md (référence)
- PLANNING_GANTT.md (suivi)
Et supprimer le reste si vous voulez.

### Q: Les fichiers sont-ils synchronisés ?
**R:** Ils sont cohérents mais indépendants. Si vous modifiez l'un, pensez à modifier les autres.

---

## 🔄 Workflow & Organisation

### Q: Dois-je utiliser un project board ?
**R:** Fortement recommandé ! Créez un Kanban sur GitHub avec :
- To Do
- In Progress
- In Review
- Done

### Q: Comment organiser l'équipe ?
**R:** Suggestion pour 3 dev :
- **Dev 1 :** Back-end CMS & Rendez-vous
- **Dev 2 :** Analytics & Newsletter
- **Dev 3 :** Espace client & Abonnements

### Q: Daily standup recommandé ?
**R:** Oui, chaque matin à 9h :
- Qu'ai-je fait hier ?
- Que vais-je faire aujourd'hui ?
- Ai-je des blocages ?

### Q: Quelle méthodologie utiliser ?
**R:** Le planning suggère 3 sprints d'une semaine (Scrum), mais adaptez à vos préférences.

---

## 🎯 Après Création

### Q: Comment vérifier que tout est créé ?
**R:** 
1. Allez sur GitHub → Issues
2. Vérifiez : 20 issues créées
3. Vérifiez : Labels présents
4. Vérifiez : Milestone "Launch v1.0" existe

Ou en ligne de commande :
```bash
gh issue list --repo donaldte/tech-articles
```

### Q: Puis-je modifier les issues après création ?
**R:** Oui ! Éditez-les directement sur GitHub comme n'importe quelle issue.

### Q: Puis-je recréer les issues si j'ai fait une erreur ?
**R:** Oui, mais :
1. Supprimez d'abord les issues existantes
2. Ou changez les titres dans le script pour éviter les doublons

### Q: Comment assigner les issues ?
**R:** Sur GitHub :
1. Ouvrez l'issue
2. Assignees → Sélectionnez le développeur
Ou en masse via l'API/CLI.

---

## 💡 Bonnes Pratiques

### Q: Dois-je créer des branches par issue ?
**R:** Oui, recommandé :
```bash
git checkout -b feature/issue-1-interface-redaction
```

### Q: Convention de nommage des branches ?
**R:** Suggestion :
- `feature/issue-N-short-description`
- `fix/issue-N-bug-description`
- `docs/issue-N-doc-description`

### Q: Code review obligatoire ?
**R:** Oui, fortement recommandé pour la qualité du code.

### Q: Tests recommandés ?
**R:** Oui :
- Tests unitaires
- Tests d'intégration
- Tests E2E pour les flows critiques

---

## 🔒 Sécurité

### Q: Puis-je commiter le token dans .env.issues ?
**R:** **NON !** Le .gitignore protège ce fichier, mais ne le committez JAMAIS.

### Q: Que faire si j'ai accidentellement commité mon token ?
**R:** 
1. **IMMÉDIATEMENT** révoquez le token sur GitHub
2. Créez un nouveau token
3. Supprimez-le de l'historique Git (git filter-branch ou BFG)
4. Forcez le push (attention, coordination avec l'équipe)

### Q: Le script peut-il voler mon token ?
**R:** Non, le code est open source dans ce repository. Vérifiez-le vous-même !

---

## 📊 Statistiques & Métriques

### Q: Comment suivre la progression ?
**R:** 
- GitHub Issues (% complété)
- Project board (colonnes)
- Milestone progress
- Velocity (issues/jour)

### Q: Quelle vélocité attendre ?
**R:** Environ 1 issue/jour en moyenne avec 3 développeurs (certaines en parallèle).

### Q: Comment mesurer la qualité ?
**R:**
- Code review comments
- Tests coverage (>80% recommandé)
- Bugs reportés
- User feedback

---

## 🌍 Internationalisation

### Q: Pourquoi certains fichiers sont en français ?
**R:** Le projet est français. Les issues seront en français sur GitHub, mais le code doit être en anglais.

### Q: Puis-je traduire en anglais ?
**R:** Oui, éditez simplement les fichiers markdown et le script Python.

---

## 🤝 Contribution

### Q: Puis-je améliorer les scripts ?
**R:** Oui ! Créez une PR avec vos améliorations.

### Q: J'ai trouvé un bug, que faire ?
**R:** Ouvrez une issue sur GitHub avec :
- Description du problème
- Étapes pour reproduire
- Environnement (OS, Python version)
- Logs d'erreur

### Q: Puis-je partager ces scripts ?
**R:** Oui, le projet est sous licence MIT (libre d'utilisation).

---

## 📞 Support

### Q: Où trouver plus d'aide ?
**R:**
- Documentation : Tous les fichiers .md
- GitHub Issues : Pour les bugs
- API GitHub : https://docs.github.com/rest
- Python Requests : https://requests.readthedocs.io/

### Q: Le script ne fonctionne toujours pas ?
**R:** Lancez le diagnostic :
```bash
./test_environment.sh
```
Et partagez la sortie dans une issue.

---

## 🎓 Ressources

### Q: Je débute avec GitHub Issues ?
**R:** Ressources :
- [GitHub Issues Guide](https://guides.github.com/features/issues/)
- [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)

### Q: Je débute avec Django ?
**R:** 
- [Django Documentation](https://docs.djangoproject.com/)
- [Cookiecutter Django](https://cookiecutter-django.readthedocs.io/)

### Q: Je veux en savoir plus sur l'API GitHub ?
**R:**
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub CLI](https://cli.github.com/)

---

**Dernière mise à jour :** 2 février 2026  
**Version :** 1.0

**Votre question n'est pas ici ?**  
Consultez [ISSUES_GUIDE.md](./ISSUES_GUIDE.md) pour le guide complet.
