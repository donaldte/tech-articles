# TUI Editor - Sample Markdown Content

This file contains sample markdown content that can be used to test the Toast UI Editor integration.

## Getting Started

When creating or editing an article page, you can copy and paste this content into the editor to see how markdown rendering works.

---

## Sample Article Content

```markdown
# Introduction to DevOps Practices

DevOps is a set of practices that combines software development (Dev) and IT operations (Ops). It aims to **shorten the systems development life cycle** and provide *continuous delivery* with high software quality.

## What is DevOps?

DevOps is about:

1. **Collaboration** - Breaking down silos between teams
2. **Automation** - Automating repetitive tasks
3. **Continuous Integration/Deployment** - Delivering code faster
4. **Monitoring** - Tracking performance and issues

### Key Benefits

- Faster time to market
- Improved collaboration
- Better quality software
- Increased efficiency

## Common Tools

| Tool | Category | Description |
|------|----------|-------------|
| Jenkins | CI/CD | Automation server |
| Docker | Containerization | Application containers |
| Kubernetes | Orchestration | Container orchestration |
| Terraform | IaC | Infrastructure as Code |

## Code Example

Here's a simple Docker configuration:

```yaml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
```

## Best Practices

> "Automate everything you can, document what you can't."
> — DevOps Principle

### Getting Started with CI/CD

To implement CI/CD in your project:

1. Set up version control (Git)
2. Create automated tests
3. Configure a CI server (Jenkins, GitHub Actions, etc.)
4. Define deployment pipelines
5. Monitor and iterate

## Links and Resources

- [Official DevOps Documentation](https://example.com/devops)
- [Docker Hub](https://hub.docker.com)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

## Conclusion

DevOps is essential for modern software development. By following these practices, you can improve your team's productivity and software quality.

**Ready to start?** Check out our [Getting Started Guide](#) to begin your DevOps journey!
```

---

## French Sample Content

```markdown
# Introduction aux Pratiques DevOps

DevOps est un ensemble de pratiques qui combine le développement logiciel (Dev) et les opérations IT (Ops). Il vise à **raccourcir le cycle de développement** et à fournir une *livraison continue* avec une haute qualité logicielle.

## Qu'est-ce que DevOps ?

DevOps concerne :

1. **Collaboration** - Briser les silos entre les équipes
2. **Automatisation** - Automatiser les tâches répétitives
3. **Intégration/Déploiement Continu** - Livrer le code plus rapidement
4. **Surveillance** - Suivre les performances et les problèmes

### Avantages Clés

- Mise sur le marché plus rapide
- Meilleure collaboration
- Logiciels de meilleure qualité
- Efficacité accrue

## Outils Courants

| Outil | Catégorie | Description |
|-------|-----------|-------------|
| Jenkins | CI/CD | Serveur d'automatisation |
| Docker | Conteneurisation | Conteneurs d'application |
| Kubernetes | Orchestration | Orchestration de conteneurs |
| Terraform | IaC | Infrastructure as Code |

## Exemple de Code

Voici une configuration Docker simple :

```yaml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
```

## Bonnes Pratiques

> "Automatisez tout ce que vous pouvez, documentez ce que vous ne pouvez pas."
> — Principe DevOps

### Démarrer avec CI/CD

Pour implémenter CI/CD dans votre projet :

1. Configurez le contrôle de version (Git)
2. Créez des tests automatisés
3. Configurez un serveur CI (Jenkins, GitHub Actions, etc.)
4. Définissez des pipelines de déploiement
5. Surveillez et itérez

---

## Conclusion

DevOps est essentiel pour le développement logiciel moderne. En suivant ces pratiques, vous pouvez améliorer la productivité de votre équipe et la qualité de vos logiciels.

**Prêt à commencer ?** Consultez notre [Guide de Démarrage](#) pour débuter votre parcours DevOps !
```

---

## Preview Content Sample

Use this for the preview_content field:

```markdown
# Quick Preview

This is a **preview** of the article content. It will be visible to users *before* they purchase access to the full article.

## What You'll Learn

- Key DevOps concepts
- Essential tools and practices
- Step-by-step implementation guide

[Continue reading to learn more...](#)
```

---

## Testing Checklist

When testing the editor, verify:

- [ ] Headers render correctly (h1, h2, h3)
- [ ] Bold and italic text works
- [ ] Lists (ordered and unordered) display properly
- [ ] Tables render with proper borders
- [ ] Code blocks have syntax highlighting
- [ ] Links are clickable
- [ ] Images display (if added)
- [ ] Quotes have proper styling
- [ ] Dark theme is applied
- [ ] Editor toolbar works in French/Spanish/English
- [ ] Form submission saves markdown correctly
- [ ] Preview pane updates in real-time
