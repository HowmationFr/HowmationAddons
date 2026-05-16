# Cerberus SMART Agent

Add-on Home Assistant officiel de Cerberus. Expose les données SMART (S.M.A.R.T.) des disques de l'hôte via une API HTTP locale, consommée par l'intégration Cerberus.

## Pourquoi ?

Home Assistant tourne dans un conteneur sans accès direct aux périphériques bloc. Cet add-on, **privilégié et local-only**, est la solution propre pour exposer `smartctl` à Cerberus. Il **ne renvoie jamais** vers un projet tiers : c'est notre composant.

## Installation

1. Paramètres → Modules complémentaires → Boutique des modules complémentaires.
2. Menu trois points → Dépôts → ajouter `https://github.com/HowmationFr/cerberus-addon` (ou le sous-chemin `addon/` du repo Cerberus principal).
3. Installer "Cerberus SMART Agent".
4. Démarrer l'add-on. L'intégration Cerberus le découvre automatiquement (hostname Docker `a0d7b954-cerberus-smart-agent` ou `localhost:8099` selon le réseau).

## Sécurité

- Pas d'authentification : l'API n'est joignable que depuis le réseau Docker interne du Supervisor (et facultativement depuis `localhost` de la machine hôte).
- Exclusivement en lecture : aucun endpoint ne modifie la configuration SMART.
- Pas de télémétrie, pas de trafic sortant.

## Endpoints

- `GET /health` → `{"ok": true, "version": "0.1.0"}`
- `GET /smart/list` → liste des périphériques détectés via `smartctl --scan`
- `GET /smart/{device}` → données SMART complètes (`smartctl -a -j /dev/{device}`)

## Limites

- Marche sur HAOS et Home Assistant Supervised.
- Container et Core nécessitent une autre approche (script natif, hors-scope cette version).
