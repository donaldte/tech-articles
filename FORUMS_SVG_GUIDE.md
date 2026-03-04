# Guide — Ajouter une illustration SVG à une catégorie de forums

Ce guide explique comment stocker, personnaliser et utiliser des icônes SVG
pour les catégories (groupes) du forum, en tirant parti de la propriété CSS
`currentColor` pour un support automatique des modes clair et sombre.

---

## Pourquoi stocker le SVG en texte brut ?

La plateforme stocke le **markup SVG brut** (dans le champ `svg_icon` du
modèle `ForumCategory`) plutôt qu'un fichier image pour plusieurs raisons :

| Avantage | Explication |
|---|---|
| **Couleur dynamique** | En utilisant `currentColor`, l'icône hérite de la couleur de texte du contexte CSS — elle s'adapte automatiquement au mode sombre/clair sans dupliquer l'asset. |
| **Taille flexible** | Un SVG inline ne nécessite pas d'attributs `width`/`height` fixes ; la taille est contrôlée par les classes CSS appliquées au conteneur. |
| **Pas de requête HTTP** | Le SVG est rendu inline dans le HTML, ce qui évite une requête réseau supplémentaire. |
| **Modification CSS complète** | `fill`, `stroke`, `stroke-width`, opacité — tout est modifiable via CSS sans nouveau fichier. |

---

## Étape 1 — Préparer l'icône SVG

### Obtenir une icône

Des icônes SVG gratuites de qualité sont disponibles sur :

- [Heroicons](https://heroicons.com/) — adapté au style de l'application
- [Phosphor Icons](https://phosphoricons.com/)
- [Lucide](https://lucide.dev/)
- [Tabler Icons](https://tabler.io/icons)
- [Feather Icons](https://feathericons.com/)

### Règles de préparation

1. **Remplacer toute couleur fixe par `currentColor`.**

   Avant :
   ```xml
   <svg fill="#3b82f6" stroke="#1e40af">…</svg>
   ```

   Après :
   ```xml
   <svg fill="currentColor" stroke="currentColor">…</svg>
   ```

2. **Supprimer les attributs `width` et `height` fixes** (ou les conserver si
   vous voulez une taille par défaut, mais ils seront de toute façon écrasés
   par CSS).

3. **Garder l'attribut `viewBox`** — il est indispensable pour le
   redimensionnement correct.

4. **S'assurer que le SVG est bien formé** : toutes les balises fermées,
   pas d'entités HTML invalides.

Exemple d'une icône correctement préparée :

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
     fill="currentColor" aria-hidden="true">
  <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
</svg>
```

---

## Étape 2 — Saisir le SVG dans l'administration Django

1. Connectez-vous à l'interface d'administration Django.
2. Naviguez vers **Forums › Forum categories**.
3. Créez ou modifiez une catégorie.
4. Dans le champ **SVG icon (raw markup)**, collez directement le markup SVG
   préparé à l'étape précédente.
5. Enregistrez.

> **Astuce :** Le champ affiche un textarea `font-mono` pour faciliter la
> lecture du markup. Vous pouvez utiliser un validateur SVG en ligne
> (ex. [validator.w3.org](https://validator.w3.org/)) pour vérifier votre
> markup avant de le coller.

---

## Étape 3 — Afficher le SVG dans un template Django

Utilisez le filtre `|safe` pour injecter le markup SVG directement dans le
HTML. **N'utilisez ce filtre que sur du contenu contrôlé en interne** (jamais
sur du contenu fourni par les utilisateurs).

```html
{# Dans votre template #}
<span class="forum-category-icon text-primary-500 dark:text-primary-300 w-8 h-8">
  {{ category.svg_icon|safe }}
</span>
```

### Contrôler la taille

Appliquez des classes Tailwind CSS (ou du CSS personnalisé) au **conteneur**
du SVG. Le SVG s'adaptera via `currentColor` et `viewBox` :

```html
{# Icône 6×6 rem avec couleur héritée #}
<span class="inline-block w-6 h-6 text-indigo-600 dark:text-indigo-400">
  {{ category.svg_icon|safe }}
</span>

{# Icône 10×10 rem, couleur orange #}
<span class="inline-block w-10 h-10 text-orange-500">
  {{ category.svg_icon|safe }}
</span>
```

### Adaptation automatique au mode sombre/clair

Grâce à `currentColor`, la couleur de l'icône suit la couleur de texte du
conteneur. Il suffit de définir des couleurs Tailwind pour les deux modes :

```html
<span class="text-slate-700 dark:text-slate-200 w-8 h-8">
  {{ category.svg_icon|safe }}
</span>
```

---

## Étape 4 — Personnalisation avancée via CSS

Si vous souhaitez contrôler `fill` et `stroke` indépendamment, vous pouvez
utiliser des propriétés CSS personnalisées dans votre SVG :

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
     fill="var(--icon-fill, currentColor)"
     stroke="var(--icon-stroke, none)">
  …
</svg>
```

Puis dans votre CSS :

```css
/* Thème clair */
.forum-category-icon {
  --icon-fill: #6366f1;
  --icon-stroke: none;
}

/* Thème sombre */
.dark .forum-category-icon {
  --icon-fill: #a5b4fc;
}
```

---

## Sécurité

- Le champ `svg_icon` est réservé aux **administrateurs** via l'interface
  Django Admin.
- Dans les templates, utilisez **toujours** `|safe` uniquement sur ce champ
  — jamais sur du contenu soumis par des utilisateurs.
- Si vous envisagez de permettre aux utilisateurs de soumettre des SVG,
  utilisez une bibliothèque de sanitisation comme
  [bleach](https://bleach.readthedocs.io/) ou
  [nh3](https://nh3.readthedocs.io/) pour filtrer les attributs dangereux
  (`<script>`, gestionnaires d'événements `on*`, etc.).

---

## Résumé rapide

```
1. Obtenir un SVG depuis Heroicons / Lucide / etc.
2. Remplacer fill="#..." et stroke="#..." par currentColor
3. Supprimer width/height fixes, conserver viewBox
4. Coller le markup dans le champ svg_icon (Admin Django)
5. Dans le template : {{ category.svg_icon|safe }} dans un <span> Tailwind
```

---

## Référence des modèles forums

Cette section documente les choix de conception des modèles principaux.

### Hiérarchie des contenus

```
ForumCategory (groupe)
  └── ForumThread (discussion / question)
        └── ThreadReply  parent=None   (réponse / answer — niveau 1)
              └── ThreadReply  parent=<reply>  (commentaire sur une réponse — niveau 2)
```

Le niveau 2 est limité à **1 degré d'imbrication** : on ne peut pas commenter un commentaire.  
La vue affiche le formulaire « commenter » uniquement sur les réponses de niveau 1.

---

### Votes : threads ET réponses (`ForumVote`)

**Pourquoi voter aussi sur le thread lui-même ?**

Sur des plateformes comme Stack Overflow, deux types de votes coexistent :

| Cible | Signal | Effet |
|---|---|---|
| **Thread** (question) | La question est bien formulée et utile à la communauté | Score visible en en-tête du thread ; les threads les plus votés remontent dans le feed |
| **Reply** (réponse) | La réponse est correcte et de qualité | Tri automatique : la meilleure réponse flotte sous la solution acceptée |

Les deux partagent le même mécanisme ±1 (`ForumVoteValue.UPVOTE = 1`, `DOWNVOTE = -1`) et la même logique toggle/switch dans l'endpoint AJAX `ForumVoteView`.

**Modèle `ForumVote`** — clé étrangère nullable vers `thread` OU `reply`, jamais les deux :

```python
# vote sur un thread
ForumVote.objects.create(thread=my_thread, voter=user, value=ForumVoteValue.UPVOTE)

# vote sur une réponse
ForumVote.objects.create(reply=my_reply, voter=user, value=ForumVoteValue.DOWNVOTE)
```

Une `CheckConstraint` en base garantit qu'exactement un des deux champs est renseigné.  
`ForumThread.votes_count` et `ThreadReply.votes_count` sont mis à jour atomiquement par la vue.

---

### Feedback sur la meilleure réponse (`ThreadReplyFeedback`)

Inspiré du widget **"Was this helpful? 👍 👎"** de GitHub, affiché sous les réponses acceptées.

| Différence | Vote (`ForumVote`) | Feedback (`ThreadReplyFeedback`) |
|---|---|---|
| Visible publiquement | ✅ (score affiché) | ❌ (visible uniquement par l'auteur du thread et le staff) |
| Influence le tri | ✅ | ❌ |
| Limité aux meilleures réponses | ❌ | Recommandé (géré en vue) |
| Optionnel avec commentaire | ❌ | ✅ (`comment` TextField) |

Usage en template :

```html
{% if reply.is_best_answer %}
<div class="helpful-widget">
  <p>{{ _("Cette réponse vous a-t-elle aidé ?") }}</p>
  <form method="post" action="{% url 'forums:reply_feedback' reply.pk %}">
    {% csrf_token %}
    <button name="value" value="helpful">👍</button>
    <button name="value" value="not_helpful">👎</button>
  </form>
</div>
{% endif %}
```

---

### Énumérations (`tech_articles/utils/enums.py`)

Toutes les énumérations du module forums sont centralisées dans `utils/enums.py` :

| Classe | Valeurs | Utilisée par |
|---|---|---|
| `ForumAccessStatus` | `pending / approved / rejected` | `ForumGroupAccess.status` |
| `ForumGroupAccessType` | `subscription / purchase` | `ForumGroupAccess.access_type` |
| `ForumVoteValue` | `1 (up) / -1 (down)` | `ForumVote.value` |
| `ForumFeedbackValue` | `helpful / not_helpful` | `ThreadReplyFeedback.value` |
