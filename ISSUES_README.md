# 📋 Documentation des Issues GitHub - Tech Articles Platform

Ce dossier contient tous les fichiers nécessaires pour créer et gérer les issues GitHub du projet Tech Articles Platform.

## 🎯 Objectif

Créer **20 issues GitHub** organisées avec échéances du 2 au 22 février 2026 pour :
- 🛠️ Dashboard Administrateur (12 issues)
- 👤 Espace Utilisateur (5 issues)

## 📚 Documentation Disponible

### 🚀 Démarrage Rapide
- **[ISSUES_SUMMARY.md](./ISSUES_SUMMARY.md)** - Vue d'ensemble et démarrage rapide en 5 minutes

### 📖 Documentation Détaillée
- **[GITHUB_ISSUES.md](./GITHUB_ISSUES.md)** - Liste complète des 20 issues avec descriptions détaillées, fonctionnalités, critères d'acceptation
- **[ISSUES_GUIDE.md](./ISSUES_GUIDE.md)** - Guide complet d'utilisation et méthodes de création
- **[PLANNING_GANTT.md](./PLANNING_GANTT.md)** - Planning visuel avec diagramme Gantt et répartition hebdomadaire

### 🛠️ Outils d'Automatisation
- **[create_github_issues.py](./create_github_issues.py)** - Script Python pour création automatique via API GitHub
- **[create_issues.sh](./create_issues.sh)** - Script bash simplifié pour faciliter l'utilisation
- **[github_issues.csv](./github_issues.csv)** - Format CSV pour import ou traitement externe

### ⚙️ Configuration
- **[requirements-issues.txt](./requirements-issues.txt)** - Dépendances Python
- **[.env.issues.example](./.env.issues.example)** - Template de configuration

## 🚀 Utilisation Rapide

### Méthode 1 : Script Automatique (Recommandé)

```bash
# 1. Installer les dépendances
pip install -r requirements-issues.txt

# 2. Configurer le token GitHub
export GITHUB_TOKEN=your_github_personal_access_token

# 3. Tester en mode dry-run (recommandé)
./create_issues.sh --dry-run

# 4. Créer les issues
./create_issues.sh --create
```

### Méthode 2 : Script Python Direct

```bash
# Avec variable d'environnement
export GITHUB_TOKEN=your_token
python create_github_issues.py --repo donaldte/tech-articles

# Avec argument
python create_github_issues.py --token your_token --repo donaldte/tech-articles

# Mode dry-run
python create_github_issues.py --repo donaldte/tech-articles --dry-run
```

### Méthode 3 : Création Manuelle

1. Ouvrir [GITHUB_ISSUES.md](./GITHUB_ISSUES.md)
2. Pour chaque issue, copier/coller dans GitHub Issues
3. Ajouter les labels et échéances

## 📊 Contenu des Issues

### Dashboard Administrateur (12 issues)

#### 📝 Gestion du Contenu (4)
- Interface de rédaction d'articles
- Affichage et contrôle des publications
- Bibliothèque de médias et ressources
- Configuration sidebar mobile

#### 📅 Rendez-vous (3)
- Gestion de la disponibilité
- Prise de rendez-vous manuelle
- Vue calendrier des rendez-vous

#### 👥 Utilisateurs & Analytics (3)
- Administration des comptes
- Statistiques de visite
- Gestion des events analytics

#### 📧 Marketing (2)
- Gestion des inscriptions newsletter
- Campagne d'email newsletter

#### 💳 Monétisation (3)
- Plans de souscription
- Affichage des souscriptions actives
- Historique des transactions

### Espace Utilisateur (5 issues)

- Gestion du profil utilisateur
- Plan de souscription
- Paiements et factures
- Prise de rendez-vous
- Accès aux articles premium

## 🗓️ Planning

**Durée totale :** 20 jours (2-22 février 2026)

| Semaine | Dates | Focus Principal | Issues |
|---------|-------|-----------------|--------|
| **1** | 2-8 fév | CMS & Fondations | 3 issues |
| **2** | 9-15 fév | RDV & Utilisateurs | 8 issues |
| **3** | 16-22 fév | Marketing & Billing | 9 issues |

Voir [PLANNING_GANTT.md](./PLANNING_GANTT.md) pour le détail.

## 🏷️ Labels

Le script crée automatiquement 25 labels :

**Catégories :** dashboard, user-space, cms, appointments, billing, subscriptions, newsletter, marketing, analytics, users, media, aws, ui/ux, mobile, calendar, tracking, transactions, invoices, content, premium, profile

**Priorités :** priority:high, priority:medium, priority:low

**Type :** enhancement

## 📋 Prérequis

### Pour le Script Automatique
- Python 3.7+
- Package `requests`
- Token GitHub avec scope `repo`

### Pour Créer un Token GitHub
1. GitHub.com → Settings
2. Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Sélectionner scope: `repo`
5. Générer et copier le token

## ✅ Vérification Post-Création

Après avoir créé les issues, vérifiez :
- [ ] 20 issues créées
- [ ] 25 labels créés
- [ ] Milestone "Launch v1.0" créé (échéance 22 fév)
- [ ] Toutes les issues ont des labels
- [ ] Toutes les issues ont une échéance
- [ ] Les descriptions sont complètes

## 📈 Suivi Recommandé

1. **Project Board** : Créer un Kanban (To Do, In Progress, Review, Done)
2. **Sprints** : Organiser en 3 sprints d'une semaine
3. **Daily Standup** : Sync quotidienne de l'équipe
4. **Code Review** : Review obligatoire avant merge
5. **Tests** : Tests automatisés pour chaque issue

## 🎯 Jalons Clés

| Date | Jalon | Livrable |
|------|-------|----------|
| **8 fév** | Fondations | CMS opérationnel |
| **15 fév** | MVP Back-Office | Dashboard complet |
| **19 fév** | MVP Front | Espace utilisateur |
| **22 fév** | **LANCEMENT** | Plateforme en production |

## 🔗 Ressources Utiles

- [Documentation Django](https://docs.djangoproject.com/)
- [Cookiecutter Django](https://cookiecutter-django.readthedocs.io/)
- [API GitHub Issues](https://docs.github.com/en/rest/issues)
- [GitHub CLI](https://cli.github.com/)

## 📞 Support

### Problèmes Courants

**Script ne fonctionne pas ?**
```bash
# Vérifier Python
python3 --version

# Installer requests
pip install requests

# Tester le token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

**Permissions insuffisantes ?**
- Vérifier que le token a le scope `repo`
- Vérifier les permissions sur le repository

**Issues déjà existantes ?**
- Le script ne créera pas de doublons
- Vérifier d'abord l'état actuel des issues

## 🔐 Sécurité

⚠️ **IMPORTANT :**
- Ne jamais commiter votre token GitHub
- Utiliser les variables d'environnement
- Limiter les permissions du token (`repo` uniquement)
- Révoquer les tokens après usage si nécessaire

## 📝 Notes

- Les estimations sont données à titre indicatif (2-3 jours/issue en moyenne)
- Adapter selon la taille de votre équipe et disponibilité
- Buffer de 20% recommandé pour les imprévus
- Certaines issues peuvent être développées en parallèle

## 🤝 Contribution

Pour améliorer cette documentation ou les scripts :
1. Créer une branche
2. Faire vos modifications
3. Tester en mode dry-run
4. Soumettre une PR

## 📄 Licence

Ce projet utilise la licence MIT (voir LICENSE).

---

**Version :** 1.0  
**Créé le :** 2 février 2026  
**Dernière mise à jour :** 2 février 2026  
**Statut :** ✅ Production Ready

Pour commencer, lisez [ISSUES_SUMMARY.md](./ISSUES_SUMMARY.md) 🚀
