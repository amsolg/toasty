# ARCHITECTURE - Toasty

## Vue d'Ensemble
Toasty est un serveur gRPC autonome fournissant un service de notification de bureau unifié pour l'écosystème d'agents local. Le service est conçu pour être "agnostique" - il ne doit pas savoir qui l'appelle, simplement exécuter l'action demandée.

## Spécifications Techniques

### Langage et Framework
- **Langage Principal :** Python 3.8+
- **Protocole de Communication :** gRPC
- **Fonctionnement :** Serveur gRPC autonome (démon)

### Dépendances Clés
- `grpcio` : Implémentation du serveur gRPC
- `grpcio-tools` : Génération du code à partir du .proto
- `windows-toasts` : Bibliothèque native Windows pour toast notifications Windows 10/11

### Point de Terminaison
- **Adresse :** `localhost:50053`
- **Sécurité :** Écoute uniquement sur localhost (pas d'exposition réseau externe)

## Définition du Service (Contrat gRPC)

**Fichier :** `proto/notifier.proto`

```protobuf
syntax = "proto3";

package toasty;

service Notifier {
  rpc SendNotification (NotificationRequest) returns (NotificationResponse);
}

message NotificationRequest {
  string title = 1;
  string message = 2;

  enum Level {
    INFO = 0;
    WARNING = 1;
    ERROR = 2;
  }
  Level level = 3;
}

message NotificationResponse {
  bool success = 1;
  string error_message = 2;
}
```

## Architecture Système

```
Client App ──gRPC──► Toasty Server ──► Windows Toast API
    │                      │
    │                      ├─ Validation des requêtes
    │                      ├─ Logging des opérations
    │                      └─ Gestion des erreurs
    │
    └─ Agents/Applications (Python/Node.js/Go/C#/...)
```

## Contraintes et Exigences

### Performances
- **Légèreté :** Empreinte mémoire minimale
- **Autonomie :** Processus indépendant des agents/déclencheurs
- **Simplicité :** Logique minimale de traitement

### Robustesse
- Gestion gracieuse des erreurs (ex: échec windows-toasts)
- Retour de NotificationResponse avec success=false et message d'erreur
- Pas de plantage du serveur en cas d'erreur

### Spécificités Plateforme
- **Optimisé pour :** Windows 10/11
- **Notifications :** Toast notifications natives du système
- **Intégration :** Action Center Windows
- **Sons :** Notifications sonores natives

## Structure des Fichiers

```
/toasty
├── proto/notifier.proto          # Définition du service gRPC
├── gen/                          # Code gRPC généré (gitignore)
│   ├── __init__.py
│   ├── notifier_pb2.py
│   └── notifier_pb2_grpc.py
├── src/
│   ├── __init__.py
│   ├── notification_logic.py     # Logique notification avec windows-toasts
│   └── server.py                 # Serveur gRPC principal
├── run_server.py                 # Script de démarrage serveur
├── test_client.py                # Client de test complet
├── quick_test.py                 # Test rapide
└── requirements.txt              # Dépendances Python
```

## Interfaces et Contrats

### API gRPC
- **Service :** `toasty.Notifier`
- **Méthode :** `SendNotification`
- **Type d'appel :** Fire-and-forget (confirmation de réception seulement)

### Validation des Données
- `title` : Requis, string non-vide
- `message` : Requis, string non-vide
- `level` : Optionnel, enum (INFO=0, WARNING=1, ERROR=2)

### Gestion d'Erreurs
- Validation des paramètres d'entrée
- Gestion des échecs de windows-toasts
- Logging des erreurs sans plantage du serveur
- Retour d'informations d'erreur au client

## Fonctionnalités Windows Natives

Le service utilise `windows-toasts` qui offre :
- Toast notifications natives Windows 10/11
- Support des niveaux de priorité avec icônes système appropriées
- Sons de notification natifs
- Intégration Action Center Windows
- Durée d'affichage configurable

## Dépendances

### Dépendances Internes
- Aucune dépendance interne à l'écosystème SAM

### Dépendances Externes
- Python 3.8+ (runtime)
- Windows 10/11 (plateforme cible)
- grpcio, grpcio-tools (communication)
- windows-toasts (notifications)