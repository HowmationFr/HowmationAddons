# Internxt WebDAV

Add-on Home Assistant qui lance [Internxt CLI](https://github.com/internxt/cli) en mode **WebDAV**, pour utiliser **Internxt Drive** comme destination des sauvegardes Home Assistant via l'intégration core [WebDAV](https://www.home-assistant.io/integrations/webdav/).

C'est un wrapper de l'image officielle `internxt/webdav` qui expose la configuration de l'add-on aux variables d'environnement attendues par cette image. Référence Internxt : <https://internxt.com/fr/webdav-rclone>.

## Pourquoi ?

L'intégration WebDAV de Home Assistant attend un endpoint WebDAV joignable sur le réseau (URL + user + mot de passe). Internxt ne propose pas d'endpoint WebDAV en tant que service hébergé — il faut le faire tourner soi-même via leur CLI. Avec cet add-on, le serveur WebDAV tourne dans le même réseau Docker que Home Assistant, sans exposition publique, et HA peut y écrire ses sauvegardes.

## Installation

1. Paramètres → Modules complémentaires → Boutique des modules complémentaires.
2. Menu trois points → Dépôts → ajouter `https://github.com/HowmationFr/HowmationAddons`.
3. Installer "Internxt WebDAV".
4. Configurer les options (voir ci-dessous) puis démarrer l'add-on.
5. Dans Home Assistant : Paramètres → Appareils & services → Ajouter une intégration → **WebDAV**. URL `http://local-internxt-webdav:3005`, username/mot de passe = ceux configurés dans l'add-on.

## Configuration

| Option | Type | Obligatoire | Description |
|---|---|---|---|
| `internxt_email` | email | oui | Adresse email du compte Internxt. |
| `internxt_password` | password | oui | Mot de passe du compte Internxt. |
| `internxt_otp_secret` | str | non | Secret TOTP base32 (visible une seule fois lors de l'activation 2FA). Permet le re-login automatique au redémarrage de l'add-on. |
| `internxt_workspace_id` | str | non | ID d'espace de travail Internxt si vous voulez cibler un workspace plutôt que votre drive personnel. |
| `webdav_username` | str | oui | Utilisateur que l'intégration WebDAV de HA enverra. Par défaut `homeassistant`. **Ne réutilisez pas votre mot de passe Internxt** ici. |
| `webdav_password` | password | oui | Mot de passe attendu côté serveur WebDAV. Générez quelque chose d'aléatoire. |
| `delete_files_permanently` | bool | non | Si activé, les fichiers supprimés via WebDAV ne sont **pas** envoyés dans la corbeille Internxt — récupération impossible. Laisser à `false` sauf besoin précis. |

Le serveur est démarré en **HTTP en clair** sur le port 3005. Le trafic est confiné au réseau Docker interne du Supervisor — pas de TLS nécessaire en interne.

## Branchement à l'intégration WebDAV de Home Assistant

Après avoir démarré l'add-on :

1. Paramètres → Appareils & services → Ajouter une intégration → rechercher **WebDAV**.
2. Champs :
   - **URL** : `http://local-internxt-webdav:3005`
     - Si ce hostname court ne fonctionne pas (variations selon les installs), essayez `http://a0d7b954-internxt-webdav:3005` (le préfixe est généré par le Supervisor — visible dans la page "Logs" de l'add-on ou via `ha addons info internxt_webdav`).
   - **Nom d'utilisateur** : valeur de `webdav_username` (par défaut `homeassistant`).
   - **Mot de passe** : valeur de `webdav_password`.
   - **Vérifier SSL** : laisser coché — sans effet en HTTP.
   - **Chemin des sauvegardes** : laisser `/` ou choisir un sous-dossier (ex. `/HomeAssistantBackups`).
3. Une fois l'intégration ajoutée, Paramètres → Système → Sauvegardes → Ajouter un emplacement → choisir l'agent WebDAV.

## Limites

- **Plafond 40 Go par fichier** côté Internxt (voir [WEBDAV.md upstream](https://github.com/internxt/cli/blob/main/WEBDAV.md)). Une sauvegarde HA complète peut s'en approcher — préférez les sauvegardes partielles si vos données sont volumineuses.
- **Architectures** : `amd64` et `aarch64` uniquement. L'image upstream `internxt/webdav` n'est pas publiée pour `armv7` (Raspberry Pi 32-bit non supporté).
- **Verbes WebDAV manquants** : Internxt n'implémente pas `COPY` ni `PROPPATCH`. L'intégration WebDAV de HA n'en a pas besoin pour fonctionner, mais des outils tiers pourraient s'en plaindre.
- **Session courte** : le token Internxt peut expirer. L'add-on se re-loggue à chaque redémarrage du conteneur — si vous voyez des erreurs 401 dans les logs, redémarrez l'add-on.

## Sécurité

- Le serveur WebDAV expose **uniquement** le réseau Docker interne du Supervisor. Le mapping `3005/tcp → 3005` dans `config.yaml` rend aussi le port joignable depuis l'hôte ; si vous n'en avez pas l'usage (par exemple si seul HA y accède via le réseau Docker), vous pouvez retirer ce mapping dans l'onglet **Réseau** de l'add-on.
- L'auth WebDAV est **forcée** (`WEBDAV_CUSTOM_AUTH=true`) — pas de mode anonyme exposé.
- Vos identifiants Internxt et WebDAV sont stockés chiffrés par le Supervisor (champs `password` / `email` du schema).
- Aucune télémétrie ajoutée par l'add-on. Les requêtes sortantes sont celles d'Internxt CLI vers l'API Internxt officielle.

## Dépannage

- **L'add-on s'arrête immédiatement** : ouvrir l'onglet "Journal" du module. Une erreur `Error: INXT_USER and INXT_PASSWORD environment variables must be set` indique que la config n'est pas remplie ou n'a pas été sauvegardée avant le démarrage.
- **`Invalid credentials`** : vérifiez email/mot de passe Internxt. Si la 2FA est active sur votre compte, le champ `internxt_otp_secret` est obligatoire.
- **HA dit "Failed to connect"** : vérifier que l'add-on est démarré, que `webdav_username` / `webdav_password` saisis dans HA correspondent à ceux de l'add-on, et que l'URL est bien `http://...` (pas `https://`).
- **Sauvegarde qui échoue à mi-chemin** : c'est probablement le plafond 40 Go. Configurer une sauvegarde partielle ou exclure les addons volumineux.
