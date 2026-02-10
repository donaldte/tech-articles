# Resource Documents Management

Cette fonctionnalité permet de gérer les documents de ressources avec upload multipart vers S3, drag & drop et support du mode popup.

## Fonctionnalités

- ✅ Upload multipart vers S3 avec URLs présignées
- ✅ Upload par chunks (5MB par défaut) pour les gros fichiers
- ✅ Barre de progression en temps réel
- ✅ Drag & drop des fichiers
- ✅ Pause/Resume des uploads
- ✅ Mode popup pour création depuis les articles
- ✅ Filtrage dynamique des articles par catégorie
- ✅ URLs signées temporaires pour téléchargement sécurisé
- ✅ Gestion des permissions (admin uniquement)
- ✅ Compteur de téléchargements
- ✅ Watermark optionnel

## Architecture

### Backend (Django)

#### Modèle
```python
ResourceDocument
├── title: str
├── description: str
├── file_key: str (S3 key)
├── file_name: str
├── file_size: int
├── content_type: str
├── access_level: str (free/premium/purchase_required)
├── article: FK(Article, optional)
├── category: FK(Category, optional)
├── uploaded_by: FK(User)
├── watermark_enabled: bool
├── download_count: int
└── is_active: bool
```

#### Vues

**CRUD Views:**
- `ResourceListView` - Liste avec filtres
- `ResourceCreateView` - Création normale
- `ResourceCreatePopupView` - Création en mode popup (JSON response)
- `ResourceUpdateView` - Édition
- `ResourceDeleteView` - Suppression (avec suppression S3)

**API Views:**
- `create_multipart_upload` - Initialiser upload S3
- `generate_presigned_urls` - Générer URLs signées pour parts
- `complete_multipart_upload` - Finaliser upload
- `abort_multipart_upload` - Annuler upload
- `generate_download_url` - Générer URL temporaire de téléchargement

**Helper Views:**
- `GetArticlesByCategoryView` - Filtrer articles par catégorie (pour formulaire dynamique)
- `GenerateResourceDownloadUrlView` - Générer URL de téléchargement avec incrémentation compteur

### Frontend (JavaScript)

#### Classes principales

**ResourceUploadManager**
Gère les uploads multipart vers S3:
```javascript
const uploadManager = new ResourceUploadManager({
    chunkSize: 5 * 1024 * 1024, // 5MB
    maxConcurrentUploads: 3,
    createEndpoint: '/dashboard/resources/api/upload/create/',
    // ...
});

// Upload un fichier
const result = await uploadManager.startUpload(inputId, file);
```

**ResourceFormHandler**
Gère le formulaire de création/édition:
```javascript
new ResourceFormHandler('resource-form', {
    isPopupMode: false,
    successUrl: '/dashboard/resources/',
    cancelUrl: '/dashboard/resources/',
});
```

**ResourcePopupOpener**
Ouvre la popup et gère la communication:
```javascript
const popupOpener = new ResourcePopupOpener({
    articleCategories: ['uuid-1', 'uuid-2'],
    onResourceCreated: (resource) => {
        console.log('Resource created:', resource);
        // Ajouter la ressource à l'article...
    }
});

popupOpener.open();
```

## Utilisation

### 1. Configuration S3

Configurer les variables d'environnement:
```python
AWS_ACCESS_KEY_ID = 'your-key'
AWS_SECRET_ACCESS_KEY = 'your-secret'
AWS_STORAGE_BUCKET_NAME = 'your-bucket'
AWS_S3_REGION_NAME = 'us-east-1'
```

### 2. Création normale

Aller sur `/dashboard/resources/create/` et:
1. Drag & drop ou sélectionner un fichier
2. Remplir les détails
3. Soumettre le formulaire
4. L'upload se fait automatiquement

### 3. Création en mode popup

Dans votre page d'article:

```html
<!-- Include scripts -->
<script src="{% static 'js/dashboard/resources/resource-popup-opener.js' %}"></script>

<script>
// Créer l'opener
const resourcePopup = new ResourcePopupOpener({
    articleCategories: ['{{ category1.pk }}', '{{ category2.pk }}'],
    onResourceCreated: function(resource) {
        // Ajouter la ressource à l'interface
        addResourceToList(resource);
    }
});

// Ouvrir la popup au clic
document.getElementById('add-resource-btn').addEventListener('click', function() {
    resourcePopup.open();
});
</script>
```

### 4. Téléchargement de ressource

```javascript
// Générer URL temporaire
const response = await fetch(`/dashboard/resources/${resourceId}/download-url/`);
const data = await response.json();

// Ouvrir le téléchargement
window.open(data.url, '_blank');
```

## Flow d'upload

1. **Client** → Initialiser upload → **Django**
2. **Django** → Créer multipart upload → **S3**
3. **S3** → Retourne uploadId et key → **Django** → **Client**
4. **Client** → Demander URLs présignées → **Django**
5. **Django** → Générer URLs présignées → **S3** → **Client**
6. **Client** → Upload chunks directement → **S3**
7. **Client** → Finaliser upload → **Django**
8. **Django** → Complete multipart → **S3**
9. **Django** → Sauvegarder metadata en DB

## Sécurité

- ✅ Authentification requise (@login_required)
- ✅ Permissions admin (AdminRequiredMixin)
- ✅ URLs signées temporaires (5 minutes par défaut)
- ✅ Validation des types de fichiers
- ✅ Limite de taille (100MB)
- ✅ CSRF protection
- ✅ Origin verification pour popup messages

## Types de fichiers supportés

- PDF (.pdf)
- Word (.doc, .docx)
- Excel (.xls, .xlsx)
- PowerPoint (.ppt, .pptx)
- Text (.txt)
- Archives (.zip, .rar)

## Performance

- Upload par chunks de 5MB
- 3 uploads concurrents maximum
- Progress bar en temps réel
- Pause/Resume disponible
- Abort automatique en cas d'erreur

## Exemple complet

```python
# Dans votre vue d'article
class ArticleCreateView(CreateView):
    # ...
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passer les catégories pour le filtre
        context['article_categories'] = Category.objects.filter(
            is_active=True
        ).values_list('pk', flat=True)
        return context
```

```html
<!-- Dans votre template -->
<button id="add-resource-btn" class="btn-primary">
    Add Resource
</button>

<div id="resources-list">
    <!-- Resources will be added here -->
</div>

<script src="{% static 'js/dashboard/resources/resource-popup-opener.js' %}"></script>
<script>
const resourcePopup = new ResourcePopupOpener({
    articleCategories: [{% for cat in article_categories %}'{{ cat }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
    onResourceCreated: function(resource) {
        // Add to list
        const listItem = `
            <div class="resource-item">
                <h4>${resource.title}</h4>
                <p>${resource.file_size_display}</p>
            </div>
        `;
        document.getElementById('resources-list').insertAdjacentHTML('beforeend', listItem);
    }
});

document.getElementById('add-resource-btn').addEventListener('click', function() {
    resourcePopup.open();
});
</script>
```

## Troubleshooting

### S3 non configuré
Vérifier les variables d'environnement AWS et relancer le serveur.

### Popup bloquée
Indiquer à l'utilisateur d'autoriser les popups pour le site.

### Upload échoue
- Vérifier les permissions S3
- Vérifier la taille du fichier (max 100MB)
- Vérifier le type de fichier

### URL de téléchargement expirée
Les URLs sont valides 5 minutes. Regénérer une nouvelle URL.

