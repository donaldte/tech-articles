# GitHub Issues pour Tech Articles Platform

> **Date de début :** 2 février 2026  
> **Date de fin du projet :** 22 février 2026  
> **Durée totale :** 20 jours

---

## 📋 Vue d'ensemble des catégories

1. **Dashboard Administrateur (Back-Office)** - 12 issues
2. **Espace Utilisateur (Client)** - 5 issues

**Total : 17 issues principales**

---

## 🛠️ DASHBOARD ADMINISTRATEUR (BACK-OFFICE)

### Catégorie : 📝 Gestion du Contenu (CMS)

#### Issue #1: Interface de Rédaction d'Articles
**Titre :** Créer l'interface de création et d'édition d'articles

**Description :**
Développer une interface complète pour la rédaction et l'édition d'articles dans le back-office administrateur.

**Fonctionnalités requises :**
- Éditeur WYSIWYG (rich text editor)
- Support pour le Markdown
- Prévisualisation en temps réel
- Gestion des métadonnées (titre, description, tags)
- Upload d'images dans l'éditeur
- Brouillons automatiques
- Statuts de publication (brouillon, publié, archivé)
- Planification de publication

**Critères d'acceptation :**
- [ ] L'administrateur peut créer un nouvel article
- [ ] L'administrateur peut éditer un article existant
- [ ] Les brouillons sont sauvegardés automatiquement
- [ ] Les articles peuvent être prévisualisés avant publication
- [ ] Les images peuvent être insérées et redimensionnées
- [ ] Les métadonnées sont correctement enregistrées

**Labels :** `enhancement`, `dashboard`, `cms`, `priority:high`  
**Échéance :** 6 février 2026  
**Estimation :** 3-4 jours

---

#### Issue #2: Affichage et Contrôle des Publications
**Titre :** Créer la liste de contrôle des articles publiés

**Description :**
Développer une vue de gestion pour afficher, filtrer et contrôler tous les articles du système.

**Fonctionnalités requises :**
- Liste paginée de tous les articles
- Filtres (par statut, auteur, date, catégorie)
- Recherche par titre/contenu
- Actions en masse (publier, archiver, supprimer)
- Statistiques par article (vues, commentaires)
- Tri personnalisé (date, popularité, titre)
- Gestion des versions

**Critères d'acceptation :**
- [ ] Tous les articles sont affichés dans une liste paginée
- [ ] Les filtres fonctionnent correctement
- [ ] Les actions en masse sont opérationnelles
- [ ] Les statistiques sont visibles pour chaque article
- [ ] L'interface est responsive

**Labels :** `enhancement`, `dashboard`, `cms`, `priority:high`  
**Échéance :** 8 février 2026  
**Estimation :** 2 jours

---

#### Issue #3: Bibliothèque de Médias et Ressources
**Titre :** Créer la bibliothèque de médias et gestion des ressources

**Description :**
Développer un système de gestion de médias pour les articles (images, vidéos, documents).

**Fonctionnalités requises :**
- Upload de fichiers multiples (drag & drop)
- Gestion des dossiers
- Prévisualisation des médias
- Métadonnées des fichiers (titre, alt text, description)
- Recherche et filtres
- Optimisation automatique des images
- Intégration avec AWS S3/CloudFront
- Gestion des documents liés aux articles

**Critères d'acceptation :**
- [ ] Les fichiers peuvent être uploadés par drag & drop
- [ ] La bibliothèque affiche tous les médias de manière organisée
- [ ] Les images sont automatiquement optimisées
- [ ] Les médias peuvent être recherchés et filtrés
- [ ] L'intégration AWS fonctionne correctement
- [ ] Les documents peuvent être associés aux articles

**Labels :** `enhancement`, `dashboard`, `media`, `aws`, `priority:medium`  
**Échéance :** 10 février 2026  
**Estimation :** 2-3 jours

---

#### Issue #4: Configuration de la Sidebar Mobile
**Titre :** Configurer l'affichage et la navigation de la sidebar mobile

**Description :**
Créer une interface de configuration pour personnaliser la sidebar mobile du dashboard.

**Fonctionnalités requises :**
- Configuration de l'ordre des éléments de menu
- Activation/désactivation de sections
- Personnalisation des icônes
- Prévisualisation en temps réel
- Gestion des permissions par rôle
- Mode sombre/clair

**Critères d'acceptation :**
- [ ] La sidebar mobile est configurable depuis le dashboard
- [ ] Les modifications sont visibles en temps réel
- [ ] Les permissions par rôle sont respectées
- [ ] L'interface est intuitive et responsive

**Labels :** `enhancement`, `dashboard`, `ui/ux`, `mobile`, `priority:low`  
**Échéance :** 12 février 2026  
**Estimation :** 1-2 jours

---

### Catégorie : 📅 Rendez-vous & Disponibilités

#### Issue #5: Gestion de la Disponibilité
**Titre :** Créer le système de paramétrage des créneaux horaires

**Description :**
Développer une interface pour gérer les disponibilités et créneaux horaires pour les rendez-vous.

**Fonctionnalités requises :**
- Configuration des heures d'ouverture par jour
- Définition de la durée des créneaux
- Gestion des exceptions (jours fériés, absences)
- Créneaux récurrents
- Limite de rendez-vous par créneau
- Fuseau horaire
- Délai de réservation minimum

**Critères d'acceptation :**
- [ ] Les créneaux peuvent être définis par jour de la semaine
- [ ] Les exceptions peuvent être ajoutées facilement
- [ ] Les modifications sont sauvegardées et appliquées immédiatement
- [ ] Le système gère correctement les fuseaux horaires
- [ ] Les limites de réservation sont respectées

**Labels :** `enhancement`, `dashboard`, `appointments`, `priority:high`  
**Échéance :** 11 février 2026  
**Estimation :** 2-3 jours

---

#### Issue #6: Prise de Rendez-vous Manuelle
**Titre :** Implémenter la capacité de réserver manuellement pour un client

**Description :**
Créer une interface pour que l'administrateur puisse prendre des rendez-vous au nom des clients.

**Fonctionnalités requises :**
- Sélection du client (recherche)
- Choix du créneau disponible
- Ajout de notes internes
- Confirmation par email automatique
- Gestion des conflits
- Modification/annulation de rendez-vous

**Critères d'acceptation :**
- [ ] L'administrateur peut rechercher un client
- [ ] Les créneaux disponibles sont affichés correctement
- [ ] Le rendez-vous peut être créé avec notes
- [ ] Un email de confirmation est envoyé
- [ ] Les conflits sont détectés et gérés

**Labels :** `enhancement`, `dashboard`, `appointments`, `priority:high`  
**Échéance :** 13 février 2026  
**Estimation :** 2 jours

---

#### Issue #7: Vue Calendrier des Rendez-vous
**Titre :** Créer la vue d'ensemble (calendrier) des rendez-vous

**Description :**
Développer une interface calendrier pour visualiser tous les rendez-vous pris.

**Fonctionnalités requises :**
- Vue jour/semaine/mois
- Affichage des détails au survol
- Filtres par statut (confirmé, en attente, annulé)
- Export au format iCal/CSV
- Intégration Google Calendar
- Notifications de rappel
- Statistiques de taux de remplissage

**Critères d'acceptation :**
- [ ] Le calendrier affiche tous les rendez-vous
- [ ] Les différentes vues (jour/semaine/mois) fonctionnent
- [ ] Les filtres sont opérationnels
- [ ] L'export fonctionne correctement
- [ ] Les statistiques sont visibles

**Labels :** `enhancement`, `dashboard`, `appointments`, `calendar`, `priority:medium`  
**Échéance :** 15 février 2026  
**Estimation :** 2-3 jours

---

### Catégorie : 👥 Utilisateurs & Analytics

#### Issue #8: Administration des Comptes Utilisateurs
**Titre :** Créer l'interface de gestion des profils utilisateurs

**Description :**
Développer une interface complète pour gérer tous les aspects des comptes utilisateurs.

**Fonctionnalités requises :**
- Liste de tous les utilisateurs
- Filtres et recherche avancée
- Modification des profils
- Gestion des rôles et permissions
- Activation/désactivation de comptes
- Historique des actions
- Réinitialisation de mot de passe
- Envoi d'emails aux utilisateurs

**Critères d'acceptation :**
- [ ] Tous les utilisateurs sont listés avec pagination
- [ ] Les profils peuvent être modifiés
- [ ] Les rôles et permissions sont gérés correctement
- [ ] L'historique des actions est visible
- [ ] Les emails peuvent être envoyés

**Labels :** `enhancement`, `dashboard`, `users`, `priority:high`  
**Échéance :** 14 février 2026  
**Estimation :** 2-3 jours

---

#### Issue #9: Statistiques de Visite et Trafic
**Titre :** Implémenter l'analyse du trafic global du site

**Description :**
Créer un tableau de bord avec des statistiques détaillées sur le trafic du site.

**Fonctionnalités requises :**
- Visiteurs uniques (jour/semaine/mois)
- Pages vues
- Durée moyenne des sessions
- Taux de rebond
- Sources de trafic
- Appareils utilisés
- Graphiques interactifs
- Export des données

**Critères d'acceptation :**
- [ ] Les statistiques de base sont affichées
- [ ] Les graphiques sont interactifs et clairs
- [ ] Les données peuvent être filtrées par période
- [ ] Les données peuvent être exportées
- [ ] Les performances sont optimales

**Labels :** `enhancement`, `dashboard`, `analytics`, `priority:medium`  
**Échéance :** 16 février 2026  
**Estimation :** 2-3 jours

---

#### Issue #10: Gestion des Events Analytics
**Titre :** Créer le système de suivi des actions spécifiques des utilisateurs

**Description :**
Développer un système pour tracker et analyser les actions spécifiques des utilisateurs.

**Fonctionnalités requises :**
- Définition d'events personnalisés
- Tracking automatique d'events clés (inscription, achat, lecture)
- Entonnoirs de conversion
- Segmentation d'utilisateurs
- Rapports personnalisés
- Alertes sur événements importants
- API pour intégrations externes

**Critères d'acceptation :**
- [ ] Les events personnalisés peuvent être définis
- [ ] Le tracking fonctionne correctement
- [ ] Les entonnoirs de conversion sont visualisables
- [ ] Les segments d'utilisateurs peuvent être créés
- [ ] Les rapports peuvent être générés

**Labels :** `enhancement`, `dashboard`, `analytics`, `tracking`, `priority:medium`  
**Échéance :** 17 février 2026  
**Estimation :** 2-3 jours

---

### Catégorie : 📧 Marketing & Newsletter

#### Issue #11: Gestion des Inscriptions Newsletter
**Titre :** Créer l'interface de gestion des abonnés à la newsletter

**Description :**
Développer une interface pour gérer la liste des abonnés à la newsletter.

**Fonctionnalités requises :**
- Liste de tous les abonnés
- Filtres et segments
- Import/export CSV
- Gestion des désabonnements
- Statuts (actif, inactif, rebond)
- Tags et catégories
- Historique d'engagement
- Conformité RGPD

**Critères d'acceptation :**
- [ ] Tous les abonnés sont listés avec pagination
- [ ] Les filtres et segments fonctionnent
- [ ] L'import/export CSV est opérationnel
- [ ] La conformité RGPD est respectée
- [ ] Les statuts sont correctement gérés

**Labels :** `enhancement`, `dashboard`, `newsletter`, `marketing`, `priority:medium`  
**Échéance :** 18 février 2026  
**Estimation :** 2 jours

---

#### Issue #12: Campagne d'Email Newsletter
**Titre :** Implémenter le système de création et envoi de mailings groupés

**Description :**
Créer une interface complète pour créer et envoyer des campagnes d'email.

**Fonctionnalités requises :**
- Éditeur d'email WYSIWYG
- Templates d'emails
- Personnalisation (nom, prénom, etc.)
- Tests A/B
- Planification d'envoi
- Gestion des pièces jointes
- Statistiques d'envoi (ouvertures, clics, désabonnements)
- Preview sur différents clients email

**Critères d'acceptation :**
- [ ] Les emails peuvent être créés avec l'éditeur
- [ ] Les templates sont utilisables
- [ ] La personnalisation fonctionne
- [ ] Les envois peuvent être planifiés
- [ ] Les statistiques sont disponibles
- [ ] Les tests A/B sont fonctionnels

**Labels :** `enhancement`, `dashboard`, `newsletter`, `marketing`, `priority:high`  
**Échéance :** 20 février 2026  
**Estimation :** 3 jours

---

### Catégorie : 💳 Monétisation & Abonnements

#### Issue #13: Plans de Souscription
**Titre :** Créer la configuration des offres d'abonnement (prix, durée)

**Description :**
Développer une interface pour créer et gérer les différents plans d'abonnement.

**Fonctionnalités requises :**
- Création de plans (nom, description, prix)
- Durée (mensuel, annuel, personnalisé)
- Fonctionnalités incluses par plan
- Essai gratuit
- Codes promo et réductions
- Limites par plan
- Activation/désactivation de plans
- Historique des modifications

**Critères d'acceptation :**
- [ ] Les plans peuvent être créés et configurés
- [ ] Les prix et durées sont gérés correctement
- [ ] Les codes promo fonctionnent
- [ ] Les limites sont appliquées
- [ ] L'historique est conservé

**Labels :** `enhancement`, `dashboard`, `billing`, `subscriptions`, `priority:high`  
**Échéance :** 19 février 2026  
**Estimation :** 2-3 jours

---

#### Issue #14: Affichage des Souscriptions Actives
**Titre :** Créer la liste des abonnés actifs et leur gestion

**Description :**
Développer une interface pour visualiser et gérer tous les abonnements actifs.

**Fonctionnalités requises :**
- Liste de tous les abonnements
- Filtres (plan, statut, date)
- Détails par abonnement
- Modification manuelle
- Annulation/suspension
- Renouvellement
- Statistiques (MRR, churn rate)
- Alertes d'expiration

**Critères d'acceptation :**
- [ ] Tous les abonnements sont listés
- [ ] Les filtres fonctionnent correctement
- [ ] Les modifications peuvent être effectuées
- [ ] Les statistiques sont calculées correctement
- [ ] Les alertes sont envoyées

**Labels :** `enhancement`, `dashboard`, `billing`, `subscriptions`, `priority:medium`  
**Échéance :** 21 février 2026  
**Estimation :** 2 jours

---

#### Issue #15: Historique des Transactions
**Titre :** Créer l'affichage de l'historique financier et paiements reçus

**Description :**
Développer une interface pour visualiser toutes les transactions financières.

**Fonctionnalités requises :**
- Liste de toutes les transactions
- Filtres (date, montant, statut, utilisateur)
- Détails par transaction
- Statuts (réussi, échoué, remboursé, en attente)
- Export comptable (CSV, PDF)
- Réconciliation bancaire
- Statistiques financières
- Rapports périodiques

**Critères d'acceptation :**
- [ ] Toutes les transactions sont listées
- [ ] Les filtres sont opérationnels
- [ ] Les exports fonctionnent correctement
- [ ] Les statistiques sont précises
- [ ] Les rapports peuvent être générés

**Labels :** `enhancement`, `dashboard`, `billing`, `transactions`, `priority:medium`  
**Échéance :** 22 février 2026  
**Estimation :** 2 jours

---

## 👤 ESPACE UTILISATEUR (CLIENT)

### Issue #16: Gestion du Profil Utilisateur
**Titre :** Créer l'interface de mise à jour des informations personnelles

**Description :**
Développer une interface pour que les utilisateurs puissent gérer leur profil.

**Fonctionnalités requises :**
- Modification des informations personnelles
- Upload de photo de profil
- Changement de mot de passe
- Préférences de notification
- Gestion de la confidentialité
- Suppression de compte
- Historique d'activité
- Connexion via réseaux sociaux

**Critères d'acceptation :**
- [ ] Les utilisateurs peuvent modifier leurs informations
- [ ] La photo de profil peut être uploadée
- [ ] Le mot de passe peut être changé en toute sécurité
- [ ] Les préférences sont sauvegardées
- [ ] La suppression de compte fonctionne (avec confirmation)

**Labels :** `enhancement`, `user-space`, `profile`, `priority:high`  
**Échéance :** 14 février 2026  
**Estimation :** 2 jours

---

#### Issue #17: Plan de Souscription Utilisateur
**Titre :** Créer l'interface de choix et gestion d'abonnement

**Description :**
Développer une interface pour que les utilisateurs puissent choisir et gérer leur abonnement.

**Fonctionnalités requises :**
- Affichage des plans disponibles
- Comparaison des plans
- Sélection et paiement
- Changement de plan (upgrade/downgrade)
- Annulation d'abonnement
- Historique des abonnements
- Notification avant renouvellement
- Gestion des moyens de paiement

**Critères d'acceptation :**
- [ ] Les plans sont affichés clairement
- [ ] L'utilisateur peut souscrire à un plan
- [ ] Le changement de plan fonctionne
- [ ] L'annulation est possible avec confirmation
- [ ] Les moyens de paiement peuvent être gérés

**Labels :** `enhancement`, `user-space`, `subscriptions`, `billing`, `priority:high`  
**Échéance :** 19 février 2026  
**Estimation :** 2-3 jours

---

#### Issue #18: Paiements et Factures
**Titre :** Créer l'historique des factures et téléchargement

**Description :**
Développer une interface pour que les utilisateurs puissent consulter et télécharger leurs factures.

**Fonctionnalités requises :**
- Liste de toutes les factures
- Téléchargement au format PDF
- Détails par facture
- Statut de paiement
- Historique des paiements
- Remboursements
- Mise à jour des informations de facturation
- Notifications de nouvelles factures

**Critères d'acceptation :**
- [ ] Toutes les factures sont listées chronologiquement
- [ ] Les factures peuvent être téléchargées en PDF
- [ ] Les détails sont complets et corrects
- [ ] Les informations de facturation peuvent être mises à jour
- [ ] Les notifications fonctionnent

**Labels :** `enhancement`, `user-space`, `billing`, `invoices`, `priority:medium`  
**Échéance :** 21 février 2026  
**Estimation :** 2 jours

---

#### Issue #19: Prise de Rendez-vous Utilisateur
**Titre :** Créer la réservation autonome sur les créneaux disponibles

**Description :**
Développer une interface pour que les utilisateurs puissent prendre des rendez-vous en autonomie.

**Fonctionnalités requises :**
- Calendrier des créneaux disponibles
- Sélection de créneau
- Formulaire de détails
- Confirmation immédiate
- Email de confirmation
- Rappels automatiques
- Modification de rendez-vous
- Annulation de rendez-vous

**Critères d'acceptation :**
- [ ] Les créneaux disponibles sont affichés
- [ ] L'utilisateur peut réserver un créneau
- [ ] La confirmation est envoyée par email
- [ ] Les rappels sont envoyés automatiquement
- [ ] La modification/annulation est possible

**Labels :** `enhancement`, `user-space`, `appointments`, `priority:high`  
**Échéance :** 13 février 2026  
**Estimation :** 2-3 jours

---

#### Issue #20: Accès aux Articles Payants
**Titre :** Créer l'accès exclusif au contenu premium

**Description :**
Développer un système pour gérer l'accès aux articles premium et payants à l'acte.

**Fonctionnalités requises :**
- Affichage des articles premium
- Achat à l'acte
- Accès basé sur l'abonnement
- Bibliothèque personnelle d'articles achetés
- Historique d'achats
- Système de favoris
- Recommandations personnalisées
- Mode lecture optimisé

**Critères d'acceptation :**
- [ ] Les articles premium sont identifiés clairement
- [ ] L'achat à l'acte fonctionne
- [ ] L'accès est correctement vérifié selon l'abonnement
- [ ] La bibliothèque personnelle est fonctionnelle
- [ ] Les recommandations sont pertinentes

**Labels :** `enhancement`, `user-space`, `content`, `premium`, `priority:high`  
**Échéance :** 9 février 2026  
**Estimation :** 2-3 jours

---

## 📊 Résumé du Planning

### Semaine 1 (2-8 février)
- Issue #1: Interface de Rédaction (échéance 6 fév)
- Issue #2: Affichage Publications (échéance 8 fév)
- Issue #20: Accès Articles Payants (échéance 9 fév - débute semaine 1)

### Semaine 2 (9-15 février)
- Issue #3: Bibliothèque Médias (échéance 10 fév)
- Issue #5: Gestion Disponibilité (échéance 11 fév)
- Issue #4: Sidebar Mobile (échéance 12 fév)
- Issue #6: Prise RDV Manuelle (échéance 13 fév)
- Issue #19: Prise RDV Utilisateur (échéance 13 fév)
- Issue #8: Administration Comptes (échéance 14 fév)
- Issue #16: Profil Utilisateur (échéance 14 fév)
- Issue #7: Vue Calendrier (échéance 15 fév)

### Semaine 3 (16-22 février)
- Issue #9: Statistiques Visite (échéance 16 fév)
- Issue #10: Events Analytics (échéance 17 fév)
- Issue #11: Gestion Newsletter (échéance 18 fév)
- Issue #13: Plans Souscription (échéance 19 fév)
- Issue #17: Plan Souscription Utilisateur (échéance 19 fév)
- Issue #12: Campagne Email (échéance 20 fév)
- Issue #14: Souscriptions Actives (échéance 21 fév)
- Issue #18: Paiements Factures (échéance 21 fév)
- Issue #15: Historique Transactions (échéance 22 fév - fin du projet)

---

## 🏷️ Labels Recommandés

Créez les labels suivants dans votre repository :
- `enhancement` - Nouvelles fonctionnalités
- `dashboard` - Back-office administrateur
- `user-space` - Espace utilisateur client
- `cms` - Gestion de contenu
- `appointments` - Rendez-vous
- `billing` - Facturation
- `subscriptions` - Abonnements
- `newsletter` - Newsletter
- `marketing` - Marketing
- `analytics` - Analytiques
- `users` - Gestion utilisateurs
- `media` - Gestion médias
- `aws` - Intégration AWS
- `ui/ux` - Interface utilisateur
- `mobile` - Mobile
- `calendar` - Calendrier
- `tracking` - Suivi
- `transactions` - Transactions
- `invoices` - Factures
- `content` - Contenu
- `premium` - Contenu premium
- `profile` - Profil utilisateur
- `priority:high` - Priorité haute
- `priority:medium` - Priorité moyenne
- `priority:low` - Priorité basse

---

## 📝 Notes d'Utilisation

### Option 1 : Création Manuelle
Copiez chaque issue ci-dessus et créez-les manuellement dans GitHub Issues en :
1. Allant sur votre repository GitHub
2. Cliquant sur "Issues" > "New Issue"
3. Remplissant le titre, la description
4. Ajoutant les labels appropriés
5. Définissant l'échéance (due date)

### Option 2 : Création via Script
Un script d'automatisation peut être créé en utilisant l'API GitHub ou GitHub CLI (`gh`).

Exemple avec GitHub CLI :
```bash
gh issue create --title "Titre de l'issue" --body "Description" --label "enhancement,dashboard" --milestone "Date limite"
```

### Option 3 : Import via CSV
GitHub permet l'import d'issues via CSV. Un fichier CSV peut être généré à partir de ces données.

---

## 🎯 Priorités Suggérées

**Très Haute Priorité (À faire en premier) :**
- Issue #1: Interface de Rédaction
- Issue #2: Affichage Publications
- Issue #5: Gestion Disponibilité
- Issue #8: Administration Comptes
- Issue #16: Profil Utilisateur
- Issue #20: Accès Articles Payants

**Haute Priorité :**
- Issue #6: Prise RDV Manuelle
- Issue #12: Campagne Email
- Issue #13: Plans Souscription
- Issue #17: Plan Souscription Utilisateur
- Issue #19: Prise RDV Utilisateur

**Priorité Moyenne :**
- Issue #3: Bibliothèque Médias
- Issue #7: Vue Calendrier
- Issue #9: Statistiques Visite
- Issue #10: Events Analytics
- Issue #11: Gestion Newsletter
- Issue #14: Souscriptions Actives
- Issue #15: Historique Transactions
- Issue #18: Paiements Factures

**Priorité Basse :**
- Issue #4: Sidebar Mobile

---

## ✅ Checklist de Démarrage

- [ ] Créer tous les labels recommandés dans le repository
- [ ] Créer un milestone "Launch v1.0" avec date limite au 22 février 2026
- [ ] Créer toutes les issues avec les bonnes échéances
- [ ] Assigner les issues aux développeurs appropriés
- [ ] Configurer un projet GitHub pour le suivi visuel (Kanban)
- [ ] Planifier les sprints si vous utilisez une méthodologie Agile
- [ ] Mettre en place les notifications pour les échéances

---

**Dernière mise à jour :** 2 février 2026
