# Article Card Component

## Description
Composant réutilisable pour afficher une carte d'article avec image, métadonnées, titre, description et badge (Gratuit/Premium).

## Utilisation

```django
{% include "tech-articles/home/includes/components/_article_card.html" with 
  image="1.jpg" 
  category="DevOps" 
  read_time=5 
  title="L' Essentiel sur Kubernetes" 
  description="Lorem ipsum dolor sit amet..." 
  is_premium=False 
  link="#" 
%}
```

## Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `image` | string | Oui | Nom du fichier image (relatif à `static/images/articles/`) |
| `category` | string | Oui | Catégorie de l'article (ex: "DevOps", "CI/CD") |
| `read_time` | int | Oui | Temps de lecture estimé en minutes |
| `title` | string | Oui | Titre de l'article |
| `description` | string | Oui | Description/extrait de l'article |
| `is_premium` | boolean | Oui | `True` pour article premium, `False` pour gratuit |
| `link` | string | Non | URL de l'article (défaut: `#`) |

## Styles CSS

Les classes CSS utilisées :
- `.article-card` : Conteneur principal avec hover effect (#252540)
- `.article-card-image` : Image avec zoom au hover
- `.article-card-badge-free` : Badge vert pour articles gratuits
- `.article-card-badge-premium` : Badge jaune pour articles premium

## Exemple complet

```django
{# Article premium #}
{% include "tech-articles/home/includes/components/_article_card.html" with 
  image="4.jpg" 
  category="Génie Logiciel" 
  read_time=30 
  title="Clean Architecture : code propre" 
  description="Lorem ipsum dolor sit amet, consectetur adipiscing elit..." 
  is_premium=True 
  link="/articles/clean-architecture" 
%}

{# Article gratuit #}
{% include "tech-articles/home/includes/components/_article_card.html" with 
  image="1.jpg" 
  category="DevOps" 
  read_time=5 
  title="L' Essentiel sur Kubernetes" 
  description="Lorem ipsum dolor sit amet, consectetur adipiscing elit..." 
  is_premium=False 
  link="/articles/kubernetes-essentiel" 
%}
```

## Internationalisation

Tous les textes sont internationalisés avec `{% trans %}` :
- "min de lecture"
- "Premium"
- "Gratuit"
- "Lire plus"

Pour ajouter des traductions :
```bash
python manage.py makemessages -l fr
python manage.py makemessages -l en
python manage.py compilemessages
```
