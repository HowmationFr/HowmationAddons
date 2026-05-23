# Howmation Add-ons

Dépôt d'add-ons officiels [Howmation](https://github.com/HowmationFr) pour Home Assistant.

## Add-ons disponibles

- [Cerberus SMART Agent](./cerberus_smart_agent) — expose les données SMART de l'hôte à l'intégration HACS Cerberus.
- [Internxt WebDAV](./internxt_webdav) — wrappe Internxt CLI en serveur WebDAV pour brancher Internxt Drive comme destination de sauvegarde de l'intégration WebDAV core de Home Assistant.

## Installation du dépôt dans Home Assistant

1. Home Assistant → **Paramètres** → **Modules complémentaires** → **Boutique des modules complémentaires**.
2. Menu **⋯** (en haut à droite) → **Dépôts**.
3. Coller `https://github.com/HowmationFr/HowmationAddons` puis **Ajouter**.
4. Les add-ons Howmation apparaissent en bas de la boutique.

## Pour les développeurs

Structure standard d'un dépôt d'add-ons HA Supervisor :

```
HowmationAddons/
├── repository.yaml             # description du dépôt (ce fichier)
├── README.md                   # ce fichier
├── cerberus_smart_agent/       # un sous-dossier par add-on
│   ├── config.yaml             # manifest de l'add-on (slug, version, options…)
│   ├── Dockerfile              # image multi-arch
│   ├── run.sh                  # entrypoint
│   ├── agent.py                # logique métier
│   └── README.md               # doc utilisateur de l'add-on
└── internxt_webdav/            # autre add-on (même structure, sans agent.py)
    ├── config.yaml
    ├── build.yaml
    ├── Dockerfile
    ├── run.sh
    └── README.md
```

Référence : <https://developers.home-assistant.io/docs/add-ons/repository>.
