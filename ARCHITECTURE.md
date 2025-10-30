# ARCHITECTURE - Toasty

## Vue d'Ensemble
Toasty est un serveur gRPC autonome fournissant un service de notification de bureau unifié pour l'écosystème d'agents SAM. Basé sur une architecture Pub/Sub avec streaming gRPC, le service implémente une taxonomie sémantique des notifications et offre des capacités interactives avancées via le système de toast Windows.

## Piliers Architecturaux Fondamentaux

### 1. Contrat Fortement Typé via Protocol Buffers
- Définition complète des structures de notification via fichiers .proto
- Source unique de vérité garantissant la cohérence entre serveur et clients
- Support de l'évolution du schéma avec rétrocompatibilité

### 2. Modèle de Communication "Push" via gRPC Streaming
- Architecture Pub/Sub utilisant le streaming côté serveur gRPC
- Notifications poussées activement vers les clients abonnés
- Latence minimisée et consommation de ressources optimisée

### 3. Séparation Claire des Responsabilités
- Couche de communication gRPC distincte du rendu d'interface utilisateur
- Composants évolutifs indépendamment
- Maintenabilité améliorée du système global

## Spécifications Techniques

### Langage et Framework
- **Langage Principal :** Python 3.8+
- **Modèle de Concurrence :** asyncio avec grpc.aio (recommandation experte)
- **Protocole de Communication :** gRPC avec streaming côté serveur
- **Fonctionnement :** Serveur gRPC asynchrone avec état (gestionnaire d'abonnés)

### Décision Architecturale Critique : asyncio vs. threading

**Recommandation Définitive : asyncio avec grpc.aio**

#### Justification Technique
Pour un serveur gRPC I/O-bound destiné à gérer de multiples connexions concurrentes d'agents locaux, asyncio présente des avantages décisifs :

- **Performance Supérieure :** Modèle mono-thread avec boucle d'événements évitant la surcharge de commutation de contexte des threads OS
- **Consommation Mémoire Réduite :** Gestion de milliers de connexions dormantes avec une empreinte minimale
- **Latence Optimisée :** Élimination de la compétition pour le GIL Python
- **Scalabilité :** Support natif pour grand nombre de connexions simultanées

#### Contrainte de Discipline
L'adoption d'asyncio impose une discipline stricte : **tout appel bloquant dans une coroutine bloquera l'ensemble de la boucle d'événements**. La logique de rendu Toast doit utiliser exclusivement des bibliothèques compatibles async.

### Dépendances Clés Optimisées
- `grpcio ≥ 1.50` : Implémentation serveur gRPC avec API asyncio
- `grpcio-tools ≥ 1.50` : Génération de code à partir du .proto
- `grpcio-health-checking` : Service de health check standardisé
- `grpcio-status` : Support du modèle d'erreur riche gRPC
- `windows-toasts ≥ 1.0` : Bibliothèque native WinRT (choix expert recommandé)
- `opentelemetry-instrumentation-grpc` : Métriques et observabilité
- `aiolimiter` : Limitation de débit async-compatible
- `asyncio, queue` : Gestion concurrence asynchrone (stdlib)

### Point de Terminaison et Sécurité

#### Modèle de Sécurité Localhost-First
- **Adresse :** `localhost:50053` (aucune exposition réseau externe)
- **Principe :** Priorité sur disponibilité vs. confidentialité
- **TLS :** Non requis (complexité vs. bénéfice minimal en localhost)

#### Rate Limiting comme Défense Principale
**Threat Model :** Agent local malveillant ou défaillant
- **Implémentation :** Intercepteur `aiolimiter` async-compatible
- **Granularité :** Par agent via métadonnées `x-agent-id`
- **Algorithme :** Leaky bucket pour lissage du trafic
- **Response :** `grpc.StatusCode.RESOURCE_EXHAUSTED` si limite dépassée

#### Stratégie IPC Sécurisée
1. **Identification :** UUID unique par agent dans métadonnées gRPC
2. **Isolation :** Limitation de débit indépendante par agent
3. **Confinement :** Communication strictement localhost
4. **Monitoring :** Métriques de rate limiting pour détection d'abus

## Taxonomie Sémantique des Notifications

### Catégories Fondamentales (Mappage UX → Technique)

| Catégorie Sémantique | Objectif Utilisateur | ToastScenario | Audio Recommandé | Visuels | Interactivité |
|---------------------|---------------------|---------------|------------------|---------|---------------|
| **Information/Succès** | Confirmation d'action, mise à jour non urgente | Default | Notification.Default ou Silent | Icône bleue/verte | Passive ou "Voir détails" |
| **Avertissement** | Problème potentiel, action préventive suggérée | Default | Notification.IM | Icône triangle jaune | Boutons "Ignorer"/"Plus d'infos" |
| **Critique/Erreur** | Défaillance immédiate, action requise | Alarm/Reminder | Notification.Looping.Alarm | Icône rouge, Hero image | Boutons "Accepter"/"Réessayer" |
| **Requête Interactive** | Solliciter entrée utilisateur | Default/Reminder | Notification.Reminder | Icône question bleue | Champs de saisie, menus |

### Correspondance avec Capacités Windows Toast
- **Scenario :** Contrôle la persistance et le comportement audio
- **Audio :** Sons prédéfinis Windows pour différents niveaux d'urgence
- **Éléments Visuels :** Icônes, images héroïques, barres de progression
- **Durée :** Configuration short/long selon l'importance
- **Interactivité :** Boutons, champs de saisie, menus de sélection

## Définition du Service (Contrat gRPC)

### Architecture Pub/Sub : Séparation Commande/Requête

**Fichier :** `proto/notifications.proto`

```protobuf
syntax = "proto3";
package sam.notifications.v1;

// Service principal pour publication et abonnement aux notifications
service NotificationService {
  // RPC unaire pour publier une notification (Commande)
  rpc Publish(PublishRequest) returns (PublishResponse);

  // RPC streaming pour s'abonner aux notifications (Requête)
  rpc Subscribe(SubscriptionRequest) returns (stream Notification);
}

// Messages pour les RPC
message PublishRequest {
  string target_client_id = 1;
  Notification notification = 2;
}

message PublishResponse {
  string notification_id = 1;
  bool success = 2;
}

message SubscriptionRequest {
  string client_id = 1;
}
```

### Structure Polymorphe des Notifications (oneof)

```protobuf
// Message principal avec payload polymorphe
message Notification {
  string id = 1;
  UrgencyLevel urgency = 2;
  AudioHint audio_hint = 3;
  int64 timestamp_ms = 4;

  // Payload polymorphe garantissant "une notification, un objectif"
  oneof payload {
    TextMessage text_message = 5;
    ImageTextMessage image_text_message = 6;
    InteractiveMessage interactive_message = 7;
    ProgressMessage progress_message = 8;
  }
}

enum UrgencyLevel {
  URGENCY_LEVEL_UNSPECIFIED = 0;
  INFO = 1;
  WARNING = 2;
  CRITICAL = 3;
}

enum AudioHint {
  AUDIO_HINT_UNSPECIFIED = 0;
  DEFAULT = 1;
  ALARM = 2;
  REMINDER = 3;
  SILENT = 4;
}
```

### Composants Modulaires et Réutilisables

```protobuf
// Composants de base
message Header {
  string title = 1;
  optional string subtitle = 2;
}

message Image {
  string local_path = 1;
  enum Placement {
    PLACEMENT_UNSPECIFIED = 0;
    APP_LOGO_OVERRIDE = 1;
    HERO = 2;
  }
  Placement placement = 2;
}

message Button {
  string text = 1;
  string action_id = 2;  // ID unique pour callbacks
}

message TextInput {
  string id = 1;
  string placeholder_text = 2;
}

message ProgressBar {
  string status_text = 1;
  float value = 2;  // 0.0 à 1.0
  optional string value_string_override = 3;
}

// Types de payload spécifiques
message TextMessage {
  Header header = 1;
  string body_text_line1 = 2;
  string body_text_line2 = 3;
}

message ImageTextMessage {
  Header header = 1;
  string body_text = 2;
  Image image = 3;
}

message InteractiveMessage {
  Header header = 1;
  string body_text = 2;
  repeated Button buttons = 3;
  optional TextInput text_input = 4;
}

message ProgressMessage {
  Header header = 1;
  ProgressBar progress_bar = 2;
}
```

## Architecture Système

### Modèle Pub/Sub avec Streaming gRPC

```
SAM Ecosystem Agents                    Toasty Server (avec état)
┌─────────────────────┐                ┌──────────────────────────┐
│ Agent Principal SAM │──Publish──────►│ SubscriberManager        │
│ Email Triggers      │                │ (Thread-Safe)            │
│ File Watchers      │                │   ├─ client_queues       │
│ Custom Agents      │                │   ├─ connection_manager   │
└─────────────────────┘                │   └─ message_distributor │
         │                             └──────────────────────────┘
         │                                        │
         │Subscribe (Stream)                      │
         └────────────────────────────────────────┘
                                                  │
                                        ┌─────────▼──────────┐
                                        │ NotificationService │
                                        │   ├─ Publish RPC   │
                                        │   └─ Subscribe RPC │
                                        └─────────┬──────────┘
                                                  │
                                        ┌─────────▼──────────┐
                                        │ Traduction Layer   │
                                        │ Protobuf → Toast   │
                                        └─────────┬──────────┘
                                                  │
                                        ┌─────────▼──────────┐
                                        │ Windows Toast API  │
                                        │ (windows-toasts)   │
                                        └────────────────────┘
```

### Flux de Données

1. **Abonnement :** L'agent appelle `Subscribe(client_id)` une fois au démarrage
2. **Enregistrement :** Le serveur crée une file d'attente dédiée pour cet agent
3. **Publication :** Un producteur appelle `Publish(target_client_id, notification)`
4. **Distribution :** Le serveur place le message dans la file d'attente de l'agent cible
5. **Streaming :** Le message est poussé via le flux gRPC vers l'agent
6. **Rendu :** L'agent traduit le Protobuf en toast Windows et l'affiche

## Contraintes et Exigences

### Performances et Concurrence
- **Modèle Thread-Safe :** SubscriberManager avec verrous pour accès concurrent
- **Efficacité Réseau :** Canal unique réutilisable par agent, keepalives configurés
- **Latence Minimale :** Push temps réel via streaming (< 100ms)
- **Mémoire Optimisée :** Files d'attente par client avec nettoyage automatique

### Robustesse et Fiabilité (Patterns de Production)

#### Health Checks Standardisés
- **Protocole gRPC :** Implémentation `grpc.health.v1.health` avec HealthServicer
- **Méthodes Exposées :** `Check` (unaire) et `Watch` (streaming) pour surveillance
- **États Supportés :** `SERVING`, `NOT_SERVING`, `SERVICE_UNKNOWN`
- **Intégration :** Compatible systèmes de monitoring (Kubernetes, scripts de surveillance)

#### Graceful Shutdown Pattern
**Séquence d'Arrêt Gracieux :**
1. **Capture des Signaux :** Interception SIGTERM/SIGINT via signal handlers
2. **Update Health Status :** `health_servicer.set("", HealthCheckResponse.NOT_SERVING)`
3. **Server Shutdown :** `await server.stop(grace_period_seconds=5)`
4. **Cleanup Completion :** Attendre la terminaison complète des RPC en cours

#### Gestion Avancée des Erreurs
- **Auto-Réparation :** Logique de reconnexion automatique côté client avec backoff exponentiel
- **Gestion des Déconnexions :** Nettoyage automatique des flux fermés via context callbacks
- **Tolérance aux Pannes :** Isolation des erreurs de rendu toast (pas de plantage du flux global)
- **État Éphémère :** Liste d'abonnés reconstituée au redémarrage, aucune persistence requise

### Contraintes d'Exécution Windows
- **Contexte Utilisateur Requis :** L'agent client doit s'exécuter en tant qu'utilisateur connecté
- **Limitation Service SYSTEM :** Les notifications échouent si exécutées en tant que service système
- **Images Locales Uniquement :** Pas de support HTTP, téléchargement local requis

### Spécificités Plateforme Avancées
- **Toast Scenarios :** Support Alarm/IncomingCall pour notifications critiques persistantes
- **Interactivité Complète :** Boutons, champs de saisie, callbacks avec action_id
- **Audio Contextuel :** Mapping automatique urgence → son Windows approprié
- **Éléments Visuels Riches :** Images héroïques, icônes de statut, barres de progression

## Structure des Fichiers Évoluée

```
/toasty
├── proto/
│   └── notifications.proto          # Nouveau schéma avec oneof et streaming
├── gen/                             # Code gRPC généré (gitignore)
│   ├── __init__.py
│   ├── notifications_pb2.py
│   └── notifications_pb2_grpc.py
├── src/
│   ├── __init__.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── notification_service.py  # Service gRPC avec Pub/Sub
│   │   └── subscriber_manager.py    # Gestionnaire d'abonnés thread-safe
│   ├── client/
│   │   ├── __init__.py
│   │   ├── notification_client.py   # Client gRPC avec reconnexion
│   │   └── toast_translator.py      # Couche traduction Protobuf→Toast
│   └── common/
│       ├── __init__.py
│       └── validation.py           # Validation des messages
├── examples/
│   ├── simple_publisher.py         # Exemple d'utilisation Publish
│   ├── interactive_subscriber.py   # Exemple d'abonné avec callbacks
│   └── progress_notification.py    # Exemple notifications avec progression
├── run_server.py                   # Script de démarrage serveur
├── test_integration.py             # Tests d'intégration Pub/Sub
└── requirements.txt                # Dépendances Python mises à jour
```

## Interfaces et Contrats

### API gRPC Évoluée
- **Service :** `sam.notifications.v1.NotificationService`
- **Méthodes :**
  - `Publish` : RPC unaire pour publier des notifications (fire-and-forget avec confirmation)
  - `Subscribe` : RPC streaming pour s'abonner au flux de notifications

### Stratégie d'Évolution du Schéma
- **Règles de Compatibilité :**
  - Jamais réutiliser les numéros de champ (utiliser `reserved`)
  - Nouveaux types de notification via ajout au `oneof payload`
  - Enrichissement des notifications existantes via champs `optional`
- **Versioning :** Package `sam.notifications.v1` pour évolution contrôlée

### Validation des Données Renforcée
- **Structure oneof :** Garantit qu'une seule charge utile est définie par notification
- **Composants modulaires :** Validation indépendante des Header, Image, Button, etc.
- **Contraintes métier :** ProgressBar.value entre 0.0 et 1.0, action_id unique pour les boutons

### Stratégies Avancées de Gestion d'Erreurs

#### Mapping Exceptions Python → Codes de Statut gRPC
**Pattern Recommandé :** Intercepteur centralisé pour mapping cohérent
- `ValueError` → `grpc.StatusCode.INVALID_ARGUMENT`
- `PermissionError` → `grpc.StatusCode.PERMISSION_DENIED`
- `FileNotFoundError` → `grpc.StatusCode.NOT_FOUND`
- `TimeoutError` → `grpc.StatusCode.DEADLINE_EXCEEDED`

#### Modèle d'Erreur Riche gRPC
**Implémentation via grpcio-status :**
1. **Définition des Détails :** Messages Protobuf `google.rpc.error_details_pb2`
2. **Types Standards :** `BadRequest`, `QuotaFailure`, `ResourceInfo`
3. **Construction Serveur :** `google.rpc.status_pb2.Status` avec détails empaquetés
4. **Traitement Client :** Extraction et dépaquetage des informations structurées

#### Mécanismes de Fallback pour Notifications Critiques
- **Fallback Primaire :** Log structuré en cas d'échec windows-toasts
- **Fallback Secondaire :** Notification système basique (API Win32 ancienne)
- **Fallback Ultime :** Écriture dans fichier d'alerte critique

## Fonctionnalités Windows Natives Étendues

### Capacités Toast Avancées via windows-toasts
- **Toast Scenarios :** Default, Alarm, IncomingCall, Reminder pour contrôle de persistance
- **Audio Riche :** Sons système Windows mappés selon UrgencyLevel
- **Éléments Visuels :** Images héroïques, logos d'application, icônes de statut
- **Interactivité Complète :** Boutons avec callbacks, champs de saisie, menus
- **Barres de Progression :** Affichage temps réel avec valeurs personnalisées

### Modèles d'Interaction
- **Passif :** Information/Succès avec rejet automatique
- **Actionnable :** Avertissements avec boutons "Ignorer"/"Détails"
- **Interactif :** Requêtes utilisateur avec saisie de texte et validation
- **Critique :** Notifications persistantes avec alarmes sonores en boucle

### Contraintes Techniques Windows

#### AUMID (AppUserModelID) - Critique pour Production
- **Rôle :** Identification unique de l'application pour Windows
- **Conséquences AUMID Manquant :**
  - Notifications attribuées à "PowerShell" ou "Python"
  - Échec de persistance dans le Centre d'actions
  - Problèmes d'activation des callbacks interactifs
- **Déploiement :** Enregistrement obligatoire dans Registre Windows

#### Contraintes d'Exécution et de Rendu
- **Contexte Utilisateur :** Exécution requise en session utilisateur connecté
- **Limitation Service SYSTEM :** Services système ne peuvent pas afficher notifications
- **Images Locales :** Téléchargement nécessaire pour images distantes
- **Différences Windows 10/11 :** Attribution d'application différente, test requis

#### Action Center et Intégration Shell
- **Persistance :** Intégration native pour historique et groupement
- **Focus Assist :** Respect automatique des paramètres "Ne pas déranger"
- **Callbacks :** Gestion des interactions utilisateur différées

## Dépendances Évoluées

### Dépendances Runtime Principales (Optimisées Production)
- **Python 3.8+ :** Runtime avec support asyncio et async context managers
- **Windows 10/11 :** Plateforme cible avec système de notifications moderne
- **grpcio ≥ 1.50** : Serveur gRPC avec API asyncio (grpc.aio)
- **grpcio-tools ≥ 1.50** : Génération de code Protobuf
- **grpcio-health-checking** : Health checks standardisés gRPC
- **grpcio-status** : Modèle d'erreur riche avec détails structurés
- **windows-toasts ≥ 1.0** : Notifications WinRT natives (recommandation experte)
- **opentelemetry-instrumentation-grpc** : Métriques et observabilité
- **aiolimiter** : Rate limiting compatible asyncio
- **Poetry/pip-tools** : Gestion de dépendances avec lock files

### Dépendances d'Intégration SAM
- **Aucune dépendance directe** : Service autonome accessible via gRPC uniquement
- **Contrat Protobuf** : Source unique de vérité pour l'intégration écosystème

## Observabilité et Monitoring

### Métriques avec OpenTelemetry et Prometheus
**Standards de l'Industrie pour Instrumentation :**
- **OpenTelemetry gRPC Interceptor :** Collecte automatique des métriques standards
- **Métriques Clés :**
  - Latence des requêtes (durée des appels RPC)
  - Nombre total de requêtes et taux d'erreur
  - Distribution des codes de statut gRPC
- **Export Prometheus :** Endpoint HTTP `/metrics` pour scraping

### Journalisation Structurée
**Format JSON Recommandé :**
- **Champs de Contexte :** Nom méthode RPC, adresse client, trace_id
- **Niveaux :** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Compatibilité :** ELK Stack, Splunk, systèmes de centralisation de logs

### Traçage Distribué (Optionnel)
- **Context Propagation :** trace_id via métadonnées gRPC
- **Visibilité Bout-en-Bout :** Cycle de vie notification depuis agent jusqu'à affichage
- **Intégration :** Jaeger, Zipkin pour systèmes distribués étendus

## Considérations de Performance et Déploiement

### Optimisations Localhost Expertes
- **Canal Unique :** Réutilisation de connexion TCP/HTTP2 par agent (antipattern: nouveau canal par requête)
- **Keepalives :** Ping périodique (5min) pour détection rapide des connexions fermées
- **asyncio Event Loop :** Configuration optimisée pour workload I/O-bound
- **Mémoire :** Nettoyage automatique des abonnés déconnectés via context callbacks

### Gestion des Notifications à Haut Volume
**Pattern Anti-Spam :**
- **File d'Attente :** `asyncio.Queue` pour bufferisation des requêtes
- **Coalescence :** Regroupement notifications similaires ("3 erreurs détectées")
- **Déduplication :** Suppression des notifications identiques répétées
- **Priorisation :** Notifications critiques traitées en premier

### Métriques de Performance Cibles
- **Latence :** < 100ms de l'appel Publish à l'affichage toast
- **Throughput :** Support 50+ agents simultanés sur localhost
- **Mémoire :** < 50MB empreinte serveur avec 20 abonnés actifs
- **Fiabilité :** 99.9% de succès des notifications en conditions normales

## Déploiement et Versioning

### Stratégie de Versioning
**Protobuf Versioning :**
- **Package Versionné :** `sam.notifications.v1` pour évolution contrôlée
- **Règles de Compatibilité :** Pas de réutilisation numéros de champ, ajouts via `optional`
- **Migration Path :** Support v1 et v2 simultané pendant transitions

**Dépendances Verrouillées :**
- **Poetry/pip-tools :** Lock files pour environnements reproductibles
- **Versions Épinglées :** Éviter "dependency hell" entre grpcio/protobuf/windows-toasts
- **Environnements Isolés :** venv/conda pour éviter conflits système

### Configuration de Déploiement Windows

#### Exigences AUMID
**Étapes Critiques de Déploiement :**
1. **Enregistrement Registre :** Script `register_hkey_aumid.py` obligatoire
2. **Privilèges Administrateur :** Requis pour modification registre
3. **Packaging :** Installateur MSI recommandé pour automatisation
4. **Validation :** Tests sur Windows 10 ET 11 (comportements différents)

#### Service vs. Application Utilisateur
**Recommandation :** Application utilisateur (pas de service système)
- **Contrainte Technique :** Services SYSTEM ne peuvent pas afficher notifications
- **Pattern de Démarrage :** Auto-start via Tâche Planifiée utilisateur
- **Gestion du Cycle de Vie :** Redémarrage automatique en cas de crash

### Monitoring de Production
**Surveillance Recommandée :**
- **Health Checks :** Endpoint gRPC standard pour monitoring externe
- **Métriques Prometheus :** Latence, taux d'erreur, nombre d'abonnés actifs
- **Logs Structurés :** JSON avec trace_id pour debugging distribué
- **Alerting :** Seuils sur latence >200ms, taux erreur >1%, down-time

Cette architecture représente l'état de l'art pour un service de notification Windows avec Python, gRPC et patterns de production robustes.