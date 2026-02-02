# Guide de Création des Issues GitHub

Ce dossier contient les ressources nécessaires pour créer rapidement toutes les issues du projet Tech Articles Platform.

## 📁 Fichiers Disponibles

### 1. `GITHUB_ISSUES.md`
Documentation complète avec :
- Description détaillée de chaque issue
- Fonctionnalités requises
- Critères d'acceptation
- Labels et échéances
- Planning par semaine
- Résumé des priorités

**Usage :** Documentation de référence et guide pour la création manuelle.

### 2. `create_github_issues.py`
Script Python automatisé pour créer toutes les issues via l'API GitHub.

**Usage :**
```bash
# Installation des dépendances
pip install requests

# Utilisation avec token en argument
python create_github_issues.py --token YOUR_GITHUB_TOKEN --repo donaldte/tech-articles

# Utilisation avec variable d'environnement (recommandé)
export GITHUB_TOKEN=your_token_here
python create_github_issues.py --repo donaldte/tech-articles

# Mode dry-run (teste sans créer)
python create_github_issues.py --repo donaldte/tech-articles --dry-run
```

**Le script va automatiquement :**
- ✅ Créer tous les labels nécessaires
- ✅ Créer le milestone "Launch v1.0" avec échéance au 22 février
- ✅ Créer les 20 issues avec leurs descriptions complètes
- ✅ Assigner les labels appropriés
- ✅ Définir les échéances

### 3. `github_issues.csv`
Fichier CSV pour import manuel ou via outils tiers.

**Colonnes :**
- `title` : Titre de l'issue
- `description` : Description condensée
- `labels` : Labels séparés par virgules
- `due_date` : Date d'échéance (format YYYY-MM-DD)
- `priority` : Priorité (High/Medium/Low)
- `category` : Catégorie de l'issue
- `estimation` : Estimation de temps

## 🚀 Méthodes de Création

### Méthode 1 : Script Python Automatisé (Recommandé)

**Avantages :**
- ✅ Rapide et automatique
- ✅ Crée labels et milestone automatiquement
- ✅ Descriptions complètes avec formatage Markdown
- ✅ Aucune erreur de saisie

**Prérequis :**
1. Python 3.7+ installé
2. Package `requests` : `pip install requests`
3. Token GitHub avec permissions `repo`

**Création du token GitHub :**
1. Aller sur GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Cliquer "Generate new token (classic)"
3. Donner un nom (ex: "Tech Articles Issues Creator")
4. Sélectionner le scope `repo` (full control of private repositories)
5. Générer et copier le token (vous ne le verrez qu'une fois !)

**Exécution :**
```bash
# Méthode 1 : Variable d'environnement (plus sûr)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
python create_github_issues.py --repo donaldte/tech-articles

# Méthode 2 : Argument direct
python create_github_issues.py --token ghp_xxxxxxxxxxxxxxxxxxxx --repo donaldte/tech-articles

# Test sans créer (dry-run)
python create_github_issues.py --repo donaldte/tech-articles --dry-run
```

### Méthode 2 : GitHub CLI (Alternative)

Si vous avez installé [GitHub CLI](https://cli.github.com/), vous pouvez créer les issues en ligne de commande :

```bash
# Authentification
gh auth login

# Créer une issue
gh issue create \
  --repo donaldte/tech-articles \
  --title "Créer l'interface de création et d'édition d'articles" \
  --body "$(cat issue_body.txt)" \
  --label "enhancement,dashboard,cms,priority:high"
```

### Méthode 3 : Création Manuelle

**Étapes :**
1. Ouvrir `GITHUB_ISSUES.md`
2. Pour chaque issue :
   - Aller sur GitHub.com → votre repo → Issues → New Issue
   - Copier/coller le titre
   - Copier/coller la description
   - Ajouter les labels (créer ceux qui n'existent pas)
   - Définir la date d'échéance (due date)
   - Créer l'issue

**Inconvénients :**
- ❌ Long (20 issues à créer)
- ❌ Risque d'erreurs
- ❌ Besoin de créer les labels manuellement

### Méthode 4 : Import CSV (via outils tiers)

Certains outils permettent d'importer des issues depuis un CSV :
- [GitHub Issues Import](https://github.com/IQAndreas/github-issues-import)
- [Ghi](https://github.com/stephencelis/ghi)
- Extensions/Add-ons de navigateur

## 📋 Labels à Créer

Si vous créez les issues manuellement, créez d'abord ces labels dans votre repository :

```
enhancement     - #a2eeef - Nouvelles fonctionnalités
dashboard       - #0052CC - Back-office administrateur
user-space      - #5319E7 - Espace utilisateur client
cms             - #1D76DB - Gestion de contenu
appointments    - #FF6B6B - Rendez-vous
billing         - #0E8A16 - Facturation
subscriptions   - #FBCA04 - Abonnements
newsletter      - #D4C5F9 - Newsletter
marketing       - #E99695 - Marketing
analytics       - #006B75 - Analytiques
users           - #BFD4F2 - Gestion utilisateurs
media           - #C5DEF5 - Gestion médias
aws             - #FF9800 - Intégration AWS
ui/ux           - #F9D0C4 - Interface utilisateur
mobile          - #FEF2C0 - Mobile
calendar        - #C2E0C6 - Calendrier
tracking        - #BFD4F2 - Suivi
transactions    - #0E8A16 - Transactions
invoices        - #D4C5F9 - Factures
content         - #1D76DB - Contenu
premium         - #FFD700 - Contenu premium
profile         - #5319E7 - Profil utilisateur
priority:high   - #D73A4A - Priorité haute
priority:medium - #FBCA04 - Priorité moyenne
priority:low    - #0E8A16 - Priorité basse
```

## 📊 Milestone

Créez un milestone nommé **"Launch v1.0 - Tech Articles Platform"** avec :
- **Date limite :** 22 février 2026
- **Description :** Lancement de la plateforme Tech Articles avec toutes les fonctionnalités principales

## 📅 Planning Recommandé

### Semaine 1 (2-8 février)
Focus sur les fondations CMS et contenu premium :
- Interface de rédaction d'articles
- Affichage et contrôle des publications
- Accès aux articles payants (début)

### Semaine 2 (9-15 février)
Développement des fonctionnalités principales :
- Bibliothèque de médias
- Système de rendez-vous complet
- Gestion des utilisateurs et profils

### Semaine 3 (16-22 février)
Finalisation avec analytics, marketing et monétisation :
- Analytics et tracking
- Newsletter et campagnes email
- Système d'abonnements complet
- Facturation et transactions

## 🎯 Priorités

### Très Haute Priorité (À faire en premier)
Les issues fondamentales pour le MVP :
1. Interface de Rédaction d'Articles
2. Affichage des Publications
3. Gestion de la Disponibilité
4. Administration des Comptes
5. Profil Utilisateur
6. Accès Articles Payants

### Haute Priorité
Fonctionnalités essentielles :
- Prise de RDV (admin et utilisateur)
- Campagne Email Newsletter
- Plans de Souscription
- Plan Souscription Utilisateur

### Priorité Moyenne
Amélioration de l'expérience :
- Bibliothèque de Médias
- Vue Calendrier
- Analytics et Statistiques
- Gestion Newsletter
- Transactions et Factures

### Priorité Basse
Nice-to-have :
- Configuration Sidebar Mobile

## 🔍 Vérification Après Création

Après avoir créé les issues, vérifiez :

- [ ] 20 issues créées au total
- [ ] Toutes les issues ont un titre clair
- [ ] Les descriptions sont complètes
- [ ] Les labels sont correctement assignés
- [ ] Les échéances sont définies
- [ ] Le milestone "Launch v1.0" est créé
- [ ] Les issues sont assignées au milestone

## 🤝 Organisation du Travail

### Suggestions :
1. **Créer un Project Board** (Kanban)
   - Colonnes : To Do, In Progress, In Review, Done
   - Lier toutes les issues au board

2. **Assignation des Issues**
   - Assigner selon les compétences (frontend, backend, fullstack)
   - Équilibrer la charge de travail

3. **Sprints**
   - Sprint 1 (2-8 fév) : CMS & Contenu
   - Sprint 2 (9-15 fév) : Rendez-vous & Utilisateurs
   - Sprint 3 (16-22 fév) : Marketing & Monétisation

4. **Daily Standup**
   - Synchronisation quotidienne
   - Identification des blocages

5. **Reviews**
   - Code review obligatoire
   - Tests avant fermeture d'issue

## 📞 Support

En cas de problème avec :
- **Le script Python :** Vérifier Python 3.7+, requests installé, token valide
- **Les permissions GitHub :** Token doit avoir scope `repo`
- **Les labels :** Le script les crée automatiquement
- **Les dates :** Format ISO 8601 (YYYY-MM-DD)

## 🔐 Sécurité

**⚠️ IMPORTANT :**
- Ne jamais commiter votre token GitHub dans le code
- Utiliser les variables d'environnement
- Révoquer les tokens après usage si nécessaire
- Limiter les permissions du token au strict nécessaire (`repo` uniquement)

## 📝 Notes

- Les estimations sont données à titre indicatif (2-3 jours par issue en moyenne)
- Adapter selon la taille de votre équipe
- Certaines issues peuvent être développées en parallèle
- Prévoir du temps pour les tests et la documentation
- Buffer recommandé de 20% pour les imprévus

---

**Dernière mise à jour :** 2 février 2026  
**Version :** 1.0
