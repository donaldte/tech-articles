#!/usr/bin/env python
"""
Script pour créer automatiquement les issues GitHub pour le projet Tech Articles.
Utilise l'API GitHub pour créer les issues avec labels et échéances.

Usage:
    python create_github_issues.py --token YOUR_GITHUB_TOKEN --repo owner/repo

Ou en utilisant la variable d'environnement:
    export GITHUB_TOKEN=your_token_here
    python create_github_issues.py --repo owner/repo
"""

import argparse
import json
import os
from datetime import datetime

import requests


class GitHubIssueCreator:
    """Classe pour créer des issues GitHub via l'API."""

    def __init__(self, token, repo):
        self.token = token
        self.repo = repo
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def create_label(self, name, color, description=""):
        """Crée un label s'il n'existe pas déjà."""
        url = f"{self.api_base}/repos/{self.repo}/labels"
        data = {"name": name, "color": color, "description": description}

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            print(f"✓ Label créé: {name}")
            return True
        elif response.status_code == 422:
            print(f"→ Label existe déjà: {name}")
            return True
        else:
            print(f"✗ Erreur création label {name}: {response.status_code}")
            print(response.json())
            return False

    def create_milestone(self, title, due_date, description=""):
        """Crée un milestone."""
        url = f"{self.api_base}/repos/{self.repo}/milestones"
        data = {
            "title": title,
            "due_on": due_date,
            "description": description,
        }

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            print(f"✓ Milestone créé: {title}")
            return response.json()["number"]
        else:
            # Vérifier si le milestone existe déjà
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                milestones = response.json()
                for ms in milestones:
                    if ms["title"] == title:
                        print(f"→ Milestone existe déjà: {title}")
                        return ms["number"]
            print(f"✗ Erreur création milestone {title}: {response.status_code}")
            return None

    def create_issue(self, title, body, labels, due_date, milestone=None):
        """Crée une issue GitHub."""
        url = f"{self.api_base}/repos/{self.repo}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": labels,
        }

        if milestone:
            data["milestone"] = milestone

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            issue_number = response.json()["number"]
            print(f"✓ Issue #{issue_number} créée: {title}")
            return issue_number
        else:
            print(f"✗ Erreur création issue '{title}': {response.status_code}")
            print(response.json())
            return None


def setup_labels(creator):
    """Crée tous les labels nécessaires."""
    labels = [
        ("enhancement", "a2eeef", "Nouvelles fonctionnalités"),
        ("dashboard", "0052CC", "Back-office administrateur"),
        ("user-space", "5319E7", "Espace utilisateur client"),
        ("cms", "1D76DB", "Gestion de contenu"),
        ("appointments", "FF6B6B", "Rendez-vous"),
        ("billing", "0E8A16", "Facturation"),
        ("subscriptions", "FBCA04", "Abonnements"),
        ("newsletter", "D4C5F9", "Newsletter"),
        ("marketing", "E99695", "Marketing"),
        ("analytics", "006B75", "Analytiques"),
        ("users", "BFD4F2", "Gestion utilisateurs"),
        ("media", "C5DEF5", "Gestion médias"),
        ("aws", "FF9800", "Intégration AWS"),
        ("ui/ux", "F9D0C4", "Interface utilisateur"),
        ("mobile", "FEF2C0", "Mobile"),
        ("calendar", "C2E0C6", "Calendrier"),
        ("tracking", "BFD4F2", "Suivi"),
        ("transactions", "0E8A16", "Transactions"),
        ("invoices", "D4C5F9", "Factures"),
        ("content", "1D76DB", "Contenu"),
        ("premium", "FFD700", "Contenu premium"),
        ("profile", "5319E7", "Profil utilisateur"),
        ("priority:high", "D73A4A", "Priorité haute"),
        ("priority:medium", "FBCA04", "Priorité moyenne"),
        ("priority:low", "0E8A16", "Priorité basse"),
    ]

    print("\n🏷️  Création des labels...")
    for name, color, description in labels:
        creator.create_label(name, color, description)


def get_issues_data():
    """Retourne la liste des issues à créer."""
    return [
        {
            "title": "Créer l'interface de création et d'édition d'articles",
            "body": """## Description
Développer une interface complète pour la rédaction et l'édition d'articles dans le back-office administrateur.

## Fonctionnalités requises
- Éditeur WYSIWYG (rich text editor)
- Support pour le Markdown
- Prévisualisation en temps réel
- Gestion des métadonnées (titre, description, tags)
- Upload d'images dans l'éditeur
- Brouillons automatiques
- Statuts de publication (brouillon, publié, archivé)
- Planification de publication

## Critères d'acceptation
- [ ] L'administrateur peut créer un nouvel article
- [ ] L'administrateur peut éditer un article existant
- [ ] Les brouillons sont sauvegardés automatiquement
- [ ] Les articles peuvent être prévisualisés avant publication
- [ ] Les images peuvent être insérées et redimensionnées
- [ ] Les métadonnées sont correctement enregistrées

## Estimation
3-4 jours
""",
            "labels": ["enhancement", "dashboard", "cms", "priority:high"],
            "due_date": "2026-02-06",
        },
        {
            "title": "Créer la liste de contrôle des articles publiés",
            "body": """## Description
Développer une vue de gestion pour afficher, filtrer et contrôler tous les articles du système.

## Fonctionnalités requises
- Liste paginée de tous les articles
- Filtres (par statut, auteur, date, catégorie)
- Recherche par titre/contenu
- Actions en masse (publier, archiver, supprimer)
- Statistiques par article (vues, commentaires)
- Tri personnalisé (date, popularité, titre)
- Gestion des versions

## Critères d'acceptation
- [ ] Tous les articles sont affichés dans une liste paginée
- [ ] Les filtres fonctionnent correctement
- [ ] Les actions en masse sont opérationnelles
- [ ] Les statistiques sont visibles pour chaque article
- [ ] L'interface est responsive

## Estimation
2 jours
""",
            "labels": ["enhancement", "dashboard", "cms", "priority:high"],
            "due_date": "2026-02-08",
        },
        {
            "title": "Créer la bibliothèque de médias et gestion des ressources",
            "body": """## Description
Développer un système de gestion de médias pour les articles (images, vidéos, documents).

## Fonctionnalités requises
- Upload de fichiers multiples (drag & drop)
- Gestion des dossiers
- Prévisualisation des médias
- Métadonnées des fichiers (titre, alt text, description)
- Recherche et filtres
- Optimisation automatique des images
- Intégration avec AWS S3/CloudFront
- Gestion des documents liés aux articles

## Critères d'acceptation
- [ ] Les fichiers peuvent être uploadés par drag & drop
- [ ] La bibliothèque affiche tous les médias de manière organisée
- [ ] Les images sont automatiquement optimisées
- [ ] Les médias peuvent être recherchés et filtrés
- [ ] L'intégration AWS fonctionne correctement
- [ ] Les documents peuvent être associés aux articles

## Estimation
2-3 jours
""",
            "labels": ["enhancement", "dashboard", "media", "aws", "priority:medium"],
            "due_date": "2026-02-10",
        },
        {
            "title": "Configurer l'affichage et la navigation de la sidebar mobile",
            "body": """## Description
Créer une interface de configuration pour personnaliser la sidebar mobile du dashboard.

## Fonctionnalités requises
- Configuration de l'ordre des éléments de menu
- Activation/désactivation de sections
- Personnalisation des icônes
- Prévisualisation en temps réel
- Gestion des permissions par rôle
- Mode sombre/clair

## Critères d'acceptation
- [ ] La sidebar mobile est configurable depuis le dashboard
- [ ] Les modifications sont visibles en temps réel
- [ ] Les permissions par rôle sont respectées
- [ ] L'interface est intuitive et responsive

## Estimation
1-2 jours
""",
            "labels": ["enhancement", "dashboard", "ui/ux", "mobile", "priority:low"],
            "due_date": "2026-02-12",
        },
        {
            "title": "Créer le système de paramétrage des créneaux horaires",
            "body": """## Description
Développer une interface pour gérer les disponibilités et créneaux horaires pour les rendez-vous.

## Fonctionnalités requises
- Configuration des heures d'ouverture par jour
- Définition de la durée des créneaux
- Gestion des exceptions (jours fériés, absences)
- Créneaux récurrents
- Limite de rendez-vous par créneau
- Fuseau horaire
- Délai de réservation minimum

## Critères d'acceptation
- [ ] Les créneaux peuvent être définis par jour de la semaine
- [ ] Les exceptions peuvent être ajoutées facilement
- [ ] Les modifications sont sauvegardées et appliquées immédiatement
- [ ] Le système gère correctement les fuseaux horaires
- [ ] Les limites de réservation sont respectées

## Estimation
2-3 jours
""",
            "labels": ["enhancement", "dashboard", "appointments", "priority:high"],
            "due_date": "2026-02-11",
        },
        {
            "title": "Implémenter la capacité de réserver manuellement pour un client",
            "body": """## Description
Créer une interface pour que l'administrateur puisse prendre des rendez-vous au nom des clients.

## Fonctionnalités requises
- Sélection du client (recherche)
- Choix du créneau disponible
- Ajout de notes internes
- Confirmation par email automatique
- Gestion des conflits
- Modification/annulation de rendez-vous

## Critères d'acceptation
- [ ] L'administrateur peut rechercher un client
- [ ] Les créneaux disponibles sont affichés correctement
- [ ] Le rendez-vous peut être créé avec notes
- [ ] Un email de confirmation est envoyé
- [ ] Les conflits sont détectés et gérés

## Estimation
2 jours
""",
            "labels": ["enhancement", "dashboard", "appointments", "priority:high"],
            "due_date": "2026-02-13",
        },
        {
            "title": "Créer la vue d'ensemble (calendrier) des rendez-vous",
            "body": """## Description
Développer une interface calendrier pour visualiser tous les rendez-vous pris.

## Fonctionnalités requises
- Vue jour/semaine/mois
- Affichage des détails au survol
- Filtres par statut (confirmé, en attente, annulé)
- Export au format iCal/CSV
- Intégration Google Calendar
- Notifications de rappel
- Statistiques de taux de remplissage

## Critères d'acceptation
- [ ] Le calendrier affiche tous les rendez-vous
- [ ] Les différentes vues (jour/semaine/mois) fonctionnent
- [ ] Les filtres sont opérationnels
- [ ] L'export fonctionne correctement
- [ ] Les statistiques sont visibles

## Estimation
2-3 jours
""",
            "labels": [
                "enhancement",
                "dashboard",
                "appointments",
                "calendar",
                "priority:medium",
            ],
            "due_date": "2026-02-15",
        },
        {
            "title": "Créer l'interface de gestion des profils utilisateurs",
            "body": """## Description
Développer une interface complète pour gérer tous les aspects des comptes utilisateurs.

## Fonctionnalités requises
- Liste de tous les utilisateurs
- Filtres et recherche avancée
- Modification des profils
- Gestion des rôles et permissions
- Activation/désactivation de comptes
- Historique des actions
- Réinitialisation de mot de passe
- Envoi d'emails aux utilisateurs

## Critères d'acceptation
- [ ] Tous les utilisateurs sont listés avec pagination
- [ ] Les profils peuvent être modifiés
- [ ] Les rôles et permissions sont gérés correctement
- [ ] L'historique des actions est visible
- [ ] Les emails peuvent être envoyés

## Estimation
2-3 jours
""",
            "labels": ["enhancement", "dashboard", "users", "priority:high"],
            "due_date": "2026-02-14",
        },
        {
            "title": "Implémenter l'analyse du trafic global du site",
            "body": """## Description
Créer un tableau de bord avec des statistiques détaillées sur le trafic du site.

## Fonctionnalités requises
- Visiteurs uniques (jour/semaine/mois)
- Pages vues
- Durée moyenne des sessions
- Taux de rebond
- Sources de trafic
- Appareils utilisés
- Graphiques interactifs
- Export des données

## Critères d'acceptation
- [ ] Les statistiques de base sont affichées
- [ ] Les graphiques sont interactifs et clairs
- [ ] Les données peuvent être filtrées par période
- [ ] Les données peuvent être exportées
- [ ] Les performances sont optimales

## Estimation
2-3 jours
""",
            "labels": ["enhancement", "dashboard", "analytics", "priority:medium"],
            "due_date": "2026-02-16",
        },
        {
            "title": "Créer le système de suivi des actions spécifiques des utilisateurs",
            "body": """## Description
Développer un système pour tracker et analyser les actions spécifiques des utilisateurs.

## Fonctionnalités requises
- Définition d'events personnalisés
- Tracking automatique d'events clés (inscription, achat, lecture)
- Entonnoirs de conversion
- Segmentation d'utilisateurs
- Rapports personnalisés
- Alertes sur événements importants
- API pour intégrations externes

## Critères d'acceptation
- [ ] Les events personnalisés peuvent être définis
- [ ] Le tracking fonctionne correctement
- [ ] Les entonnoirs de conversion sont visualisables
- [ ] Les segments d'utilisateurs peuvent être créés
- [ ] Les rapports peuvent être générés

## Estimation
2-3 jours
""",
            "labels": [
                "enhancement",
                "dashboard",
                "analytics",
                "tracking",
                "priority:medium",
            ],
            "due_date": "2026-02-17",
        },
        {
            "title": "Créer l'interface de gestion des abonnés à la newsletter",
            "body": """## Description
Développer une interface pour gérer la liste des abonnés à la newsletter.

## Fonctionnalités requises
- Liste de tous les abonnés
- Filtres et segments
- Import/export CSV
- Gestion des désabonnements
- Statuts (actif, inactif, rebond)
- Tags et catégories
- Historique d'engagement
- Conformité RGPD

## Critères d'acceptation
- [ ] Tous les abonnés sont listés avec pagination
- [ ] Les filtres et segments fonctionnent
- [ ] L'import/export CSV est opérationnel
- [ ] La conformité RGPD est respectée
- [ ] Les statuts sont correctement gérés

## Estimation
2 jours
""",
            "labels": [
                "enhancement",
                "dashboard",
                "newsletter",
                "marketing",
                "priority:medium",
            ],
            "due_date": "2026-02-18",
        },
        {
            "title": "Implémenter le système de création et envoi de mailings groupés",
            "body": """## Description
Créer une interface complète pour créer et envoyer des campagnes d'email.

## Fonctionnalités requises
- Éditeur d'email WYSIWYG
- Templates d'emails
- Personnalisation (nom, prénom, etc.)
- Tests A/B
- Planification d'envoi
- Gestion des pièces jointes
- Statistiques d'envoi (ouvertures, clics, désabonnements)
- Preview sur différents clients email

## Critères d'acceptation
- [ ] Les emails peuvent être créés avec l'éditeur
- [ ] Les templates sont utilisables
- [ ] La personnalisation fonctionne
- [ ] Les envois peuvent être planifiés
- [ ] Les statistiques sont disponibles
- [ ] Les tests A/B sont fonctionnels

## Estimation
3 jours
""",
            "labels": [
                "enhancement",
                "dashboard",
                "newsletter",
                "marketing",
                "priority:high",
            ],
            "due_date": "2026-02-20",
        },
        {
            "title": "Créer la configuration des offres d'abonnement (prix, durée)",
            "body": """## Description
Développer une interface pour créer et gérer les différents plans d'abonnement.

## Fonctionnalités requises
- Création de plans (nom, description, prix)
- Durée (mensuel, annuel, personnalisé)
- Fonctionnalités incluses par plan
- Essai gratuit
- Codes promo et réductions
- Limites par plan
- Activation/désactivation de plans
- Historique des modifications

## Critères d'acceptation
- [ ] Les plans peuvent être créés et configurés
- [ ] Les prix et durées sont gérés correctement
- [ ] Les codes promo fonctionnent
- [ ] Les limites sont appliquées
- [ ] L'historique est conservé

## Estimation
2-3 jours
""",
            "labels": [
                "enhancement",
                "dashboard",
                "billing",
                "subscriptions",
                "priority:high",
            ],
            "due_date": "2026-02-19",
        },
        {
            "title": "Créer la liste des abonnés actifs et leur gestion",
            "body": """## Description
Développer une interface pour visualiser et gérer tous les abonnements actifs.

## Fonctionnalités requises
- Liste de tous les abonnements
- Filtres (plan, statut, date)
- Détails par abonnement
- Modification manuelle
- Annulation/suspension
- Renouvellement
- Statistiques (MRR, churn rate)
- Alertes d'expiration

## Critères d'acceptation
- [ ] Tous les abonnements sont listés
- [ ] Les filtres fonctionnent correctement
- [ ] Les modifications peuvent être effectuées
- [ ] Les statistiques sont calculées correctement
- [ ] Les alertes sont envoyées

## Estimation
2 jours
""",
            "labels": [
                "enhancement",
                "dashboard",
                "billing",
                "subscriptions",
                "priority:medium",
            ],
            "due_date": "2026-02-21",
        },
        {
            "title": "Créer l'affichage de l'historique financier et paiements reçus",
            "body": """## Description
Développer une interface pour visualiser toutes les transactions financières.

## Fonctionnalités requises
- Liste de toutes les transactions
- Filtres (date, montant, statut, utilisateur)
- Détails par transaction
- Statuts (réussi, échoué, remboursé, en attente)
- Export comptable (CSV, PDF)
- Réconciliation bancaire
- Statistiques financières
- Rapports périodiques

## Critères d'acceptation
- [ ] Toutes les transactions sont listées
- [ ] Les filtres sont opérationnels
- [ ] Les exports fonctionnent correctement
- [ ] Les statistiques sont précises
- [ ] Les rapports peuvent être générés

## Estimation
2 jours
""",
            "labels": [
                "enhancement",
                "dashboard",
                "billing",
                "transactions",
                "priority:medium",
            ],
            "due_date": "2026-02-22",
        },
        {
            "title": "Créer l'interface de mise à jour des informations personnelles",
            "body": """## Description
Développer une interface pour que les utilisateurs puissent gérer leur profil.

## Fonctionnalités requises
- Modification des informations personnelles
- Upload de photo de profil
- Changement de mot de passe
- Préférences de notification
- Gestion de la confidentialité
- Suppression de compte
- Historique d'activité
- Connexion via réseaux sociaux

## Critères d'acceptation
- [ ] Les utilisateurs peuvent modifier leurs informations
- [ ] La photo de profil peut être uploadée
- [ ] Le mot de passe peut être changé en toute sécurité
- [ ] Les préférences sont sauvegardées
- [ ] La suppression de compte fonctionne (avec confirmation)

## Estimation
2 jours
""",
            "labels": ["enhancement", "user-space", "profile", "priority:high"],
            "due_date": "2026-02-14",
        },
        {
            "title": "Créer l'interface de choix et gestion d'abonnement",
            "body": """## Description
Développer une interface pour que les utilisateurs puissent choisir et gérer leur abonnement.

## Fonctionnalités requises
- Affichage des plans disponibles
- Comparaison des plans
- Sélection et paiement
- Changement de plan (upgrade/downgrade)
- Annulation d'abonnement
- Historique des abonnements
- Notification avant renouvellement
- Gestion des moyens de paiement

## Critères d'acceptation
- [ ] Les plans sont affichés clairement
- [ ] L'utilisateur peut souscrire à un plan
- [ ] Le changement de plan fonctionne
- [ ] L'annulation est possible avec confirmation
- [ ] Les moyens de paiement peuvent être gérés

## Estimation
2-3 jours
""",
            "labels": [
                "enhancement",
                "user-space",
                "subscriptions",
                "billing",
                "priority:high",
            ],
            "due_date": "2026-02-19",
        },
        {
            "title": "Créer l'historique des factures et téléchargement",
            "body": """## Description
Développer une interface pour que les utilisateurs puissent consulter et télécharger leurs factures.

## Fonctionnalités requises
- Liste de toutes les factures
- Téléchargement au format PDF
- Détails par facture
- Statut de paiement
- Historique des paiements
- Remboursements
- Mise à jour des informations de facturation
- Notifications de nouvelles factures

## Critères d'acceptation
- [ ] Toutes les factures sont listées chronologiquement
- [ ] Les factures peuvent être téléchargées en PDF
- [ ] Les détails sont complets et corrects
- [ ] Les informations de facturation peuvent être mises à jour
- [ ] Les notifications fonctionnent

## Estimation
2 jours
""",
            "labels": [
                "enhancement",
                "user-space",
                "billing",
                "invoices",
                "priority:medium",
            ],
            "due_date": "2026-02-21",
        },
        {
            "title": "Créer la réservation autonome sur les créneaux disponibles",
            "body": """## Description
Développer une interface pour que les utilisateurs puissent prendre des rendez-vous en autonomie.

## Fonctionnalités requises
- Calendrier des créneaux disponibles
- Sélection de créneau
- Formulaire de détails
- Confirmation immédiate
- Email de confirmation
- Rappels automatiques
- Modification de rendez-vous
- Annulation de rendez-vous

## Critères d'acceptation
- [ ] Les créneaux disponibles sont affichés
- [ ] L'utilisateur peut réserver un créneau
- [ ] La confirmation est envoyée par email
- [ ] Les rappels sont envoyés automatiquement
- [ ] La modification/annulation est possible

## Estimation
2-3 jours
""",
            "labels": ["enhancement", "user-space", "appointments", "priority:high"],
            "due_date": "2026-02-13",
        },
        {
            "title": "Créer l'accès exclusif au contenu premium",
            "body": """## Description
Développer un système pour gérer l'accès aux articles premium et payants à l'acte.

## Fonctionnalités requises
- Affichage des articles premium
- Achat à l'acte
- Accès basé sur l'abonnement
- Bibliothèque personnelle d'articles achetés
- Historique d'achats
- Système de favoris
- Recommandations personnalisées
- Mode lecture optimisé

## Critères d'acceptation
- [ ] Les articles premium sont identifiés clairement
- [ ] L'achat à l'acte fonctionne
- [ ] L'accès est correctement vérifié selon l'abonnement
- [ ] La bibliothèque personnelle est fonctionnelle
- [ ] Les recommandations sont pertinentes

## Estimation
2-3 jours
""",
            "labels": [
                "enhancement",
                "user-space",
                "content",
                "premium",
                "priority:high",
            ],
            "due_date": "2026-02-09",
        },
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Créer des issues GitHub pour le projet Tech Articles"
    )
    parser.add_argument(
        "--token",
        help="Token d'authentification GitHub (ou utiliser GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository au format owner/repo (ex: donaldte/tech-articles)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher ce qui serait créé sans créer réellement",
    )

    args = parser.parse_args()

    # Récupérer le token
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ Erreur: Token GitHub requis (--token ou GITHUB_TOKEN)")
        return 1

    print(f"\n🚀 Création des issues pour {args.repo}")
    print("=" * 60)

    if args.dry_run:
        print("\n⚠️  MODE DRY-RUN: Aucune issue ne sera créée\n")

    creator = GitHubIssueCreator(token, args.repo)

    # Créer les labels
    if not args.dry_run:
        setup_labels(creator)

    # Créer le milestone
    print("\n📅 Création du milestone...")
    milestone_number = None
    if not args.dry_run:
        milestone_number = creator.create_milestone(
            title="Launch v1.0 - Tech Articles Platform",
            due_date="2026-02-22T23:59:59Z",
            description="Lancement de la plateforme Tech Articles avec toutes les fonctionnalités principales",
        )

    # Créer les issues
    print("\n📝 Création des issues...")
    issues_data = get_issues_data()

    for i, issue in enumerate(issues_data, 1):
        print(f"\n[{i}/{len(issues_data)}] {issue['title']}")
        if args.dry_run:
            print(f"  → Labels: {', '.join(issue['labels'])}")
            print(f"  → Échéance: {issue['due_date']}")
        else:
            creator.create_issue(
                title=issue["title"],
                body=issue["body"],
                labels=issue["labels"],
                due_date=issue["due_date"],
                milestone=milestone_number,
            )

    print("\n" + "=" * 60)
    print(f"✅ Terminé! {len(issues_data)} issues {'seraient créées' if args.dry_run else 'créées'}")
    print("\n💡 Prochaines étapes:")
    print("   1. Vérifier les issues sur GitHub")
    print("   2. Assigner les issues aux développeurs")
    print("   3. Créer un projet GitHub pour le suivi (Kanban)")
    print("   4. Commencer le développement!")

    return 0


if __name__ == "__main__":
    exit(main())
