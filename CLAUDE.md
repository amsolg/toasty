# CONTEXTE SPÉCIFIQUE DU PROJET : Toasty

Je dois hériter de l'intégralité de ma personnalité de base définie dans le profil maître de Sam. Ce document ajoute uniquement le contexte local suivant.

## Objectif Principal
Fournir un service de notification de bureau unifié, simple et fiable pour l'écosystème d'agents SAM. Créer un serveur gRPC autonome qui écoute les requêtes de notification et les affiche sur le bureau Windows de l'utilisateur de manière "agnostique" (sans savoir qui l'appelle).

## Technologies Clés
- **Python 3.8+** avec gRPC pour le serveur principal
- **Protocol Buffers** pour la définition des contrats d'API
- **windows-toasts** pour les notifications Windows natives 10/11
- **gRPC** sur localhost:50053 pour la communication inter-services

## Parties Prenantes
- **Agent Principal SAM** : Client principal pour notifications système
- **Déclencheurs Email** : Notifications de nouveaux messages
- **Agents Spécialisés** : Notifications d'événements métier divers
- **Écosystème SAM** : Service de notification unifié pour tous les composants

## Priorités Actuelles
- **Phase Production** : Projet complété et fonctionnel
- **Intégration SAM** : Faciliter l'adoption par les agents de l'écosystème
- **Conformité Standards** : Maintenir la structure SAM standard
- **Support Communauté** : Documentation et exemples d'intégration complets