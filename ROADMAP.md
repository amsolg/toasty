# ROADMAP - Toasty

## Vue d'Ensemble
Toasty est un projet complété et en production. La roadmap se concentre sur l'intégration dans l'écosystème SAM et les améliorations futures potentielles.

## Phases de Développement

### Phase 1 : Développement Initial ✅ COMPLÉTÉE
**Objectifs :** Créer un service de notification gRPC fonctionnel (version basique)
**Livrables :**
- Service gRPC autonome unaire
- Notifications Windows natives simples
- API basique avec 3 niveaux
- Documentation initiale

**Critères de Succès :**
- ✅ Serveur gRPC opérationnel sur localhost:50053
- ✅ Support complet des 3 niveaux de notification
- ✅ Intégration windows-toasts réussie
- ✅ Tests fonctionnels validés
- ✅ Documentation utilisateur complète

### Phase 1.5 : Migration Architecture Avancée 🔄 NOUVELLE PHASE
**Objectifs :** Migrer vers l'architecture Pub/Sub avec streaming et notifications enrichies
**Livrables :**
- Nouveau schéma Protocol Buffers avec oneof et composants modulaires
- Service gRPC avec streaming côté serveur (Pub/Sub)
- SubscriberManager thread-safe pour gestion des abonnés
- Couche de traduction Protobuf → Toast pour notifications enrichies
- Support complet des interactions utilisateur (boutons, champs de saisie)

**Critères de Succès :**
- 🔄 Architecture asyncio + grpc.aio opérationnelle (recommandation experte)
- 🔄 Health checks et graceful shutdown implémentés
- 🔄 Rate limiting par agent avec isolation
- 🔄 Support des 4 types de notifications (Text, ImageText, Interactive, Progress)
- 🔄 Observabilité complète (métriques Prometheus, logs JSON)
- 🔄 AUMID correctement configuré pour intégration Windows native
- 🔄 Performance < 100ms validée avec 20+ agents simultanés

### Phase 2 : Intégration Écosystème SAM ⏳ REPORTÉE
**Objectifs :** Intégrer Toasty avancé dans l'écosystème d'agents SAM
**Livrables :**
- Migration des agents SAM existants vers nouvelle API streaming
- Bibliothèque client Python réutilisable pour agents SAM
- Documentation d'intégration avec exemples concrets (Text, Interactive, Progress)
- Templates de notifications standardisés pour l'écosystème

**Critères de Succès :**
- Agent principal SAM utilise les nouvelles notifications enrichies
- Support des notifications interactives pour workflows SAM
- Déclencheurs automatiques connectés avec types appropriés
- Performance < 100ms confirmée en production

### Phase 3 : Améliorations Avancées (Optionnel)
**Objectifs :** Étendre les capacités selon les retours d'usage
**Livrables Potentiels :**
- Notifications groupées et par lots pour réduire la surcharge
- Cache intelligent des images avec gestion automatique du téléchargement
- Interface de monitoring avec métriques de performance en temps réel
- Support multilingue avec templates localisés
- API REST optionnelle pour intégration non-Python

**Critères de Succès :**
- Support 100+ agents simultanés avec performance maintenue
- Fonctionnalités additionnelles opérationnelles sans impact sur l'existant
- Rétrocompatibilité Protobuf garantie
- Métriques de monitoring accessibles

## Dépendances Critiques

### Dépendances avec Autres Projets SAM
- **Agent Principal SAM :** Utilisation pour notifications système
- **Déclencheurs Email :** Notifications de nouveaux messages
- **Agents Spécialisés :** Notifications d'événements métier

### Dépendances Externes
- **Windows 10/11 :** Plateforme d'exécution
- **Python 3.8+ :** Runtime
- **windows-toasts :** Bibliothèque de notifications
- **gRPC :** Infrastructure de communication

### Prérequis d'Intégration
- Écosystème SAM opérationnel
- Agents configurés pour utiliser localhost:50053
- Documentation d'intégration disponible

## Prochaines Actions

### Actions Immédiates (Phase 1.5 - Migration Architecture Experte)
1. **Migration vers asyncio + grpc.aio**
   - Refactoring complet vers modèle asynchrone (recommandation experte)
   - Implémentation SubscriberManager async avec asyncio.Queue
   - Gestion automatique des déconnexions via context callbacks

2. **Patterns de Fiabilité Production**
   - Health checks standardisés (grpc.health.v1.health)
   - Graceful shutdown avec signal handlers (SIGTERM/SIGINT)
   - Intercepteurs pour mapping exceptions → codes gRPC

3. **Observabilité Complète**
   - OpenTelemetry intercepteur pour métriques Prometheus
   - Journalisation structurée JSON avec trace_id
   - Rate limiting par agent avec aiolimiter

4. **Couche de Traduction Enrichie**
   - Mapper messages Protobuf vers objets windows-toasts WinRT
   - Support complet boutons interactifs avec callbacks
   - Gestion AUMID et fallback mechanisms

### Actions Suivantes (Phase 2 - Intégration SAM)
1. **Bibliothèque Client Réutilisable**
   - Client Python avec reconnexion automatique
   - Templates et helpers pour types de notifications courants
   - Documentation développeur avec exemples concrets

2. **Migration Agents Existants**
   - Identifier les agents SAM utilisant l'ancienne API
   - Créer des scripts de migration assistée
   - Tests d'intégration bout-en-bout

### Actions Futures (Phase 3)
1. **Optimisations Avancées**
   - Cache intelligent des images avec TTL
   - Groupement de notifications pour réduire surcharge visuelle
   - Pool de connexions optimisé pour haute charge

2. **Monitoring et Observabilité**
   - Métriques Prometheus/Grafana intégrées
   - Logs structurés avec niveaux configurables
   - Interface web de monitoring temps réel

3. **Extensions Fonctionnelles**
   - Templates multilingues pour notifications
   - API REST complémentaire pour intégrations externes
   - Support de thèmes visuels personnalisables

## Évolution de l'Architecture

### Architecture Actuelle (Phase 1 - Complétée)
```
Client App ──gRPC Unaire──► Toasty Server ──► Windows Toast API
                             (SendNotification)
```

### Architecture Cible (Phase 1.5 - En Cours)
```
SAM Ecosystem Agents                    Toasty Server (Pub/Sub)
┌─────────────────────┐                ┌──────────────────────────┐
│ Agent Principal SAM │──Publish──────►│ SubscriberManager        │
│ Email Triggers      │                │ (Thread-Safe)            │
│ File Watchers      │                │   ├─ client_queues       │
│ Custom Agents      │                │   └─ connection_manager   │
└─────────────────────┘                └──────────────────────────┘
         │                                        │
         │Subscribe (Stream)                      ▼
         └────────────────────────────────► NotificationService
                                                  │
                                                  ▼
                                           Windows Toast API
                                         (Notifications Enrichies)
```

### Architecture Future (Phase 3 - Potentielle)
```
SAM Ecosystem
    ├── Agent Principal ──┐
    ├── Email Trigger ────┼──gRPC Streaming──► Toasty Server ────► Windows Toast API
    ├── File Watcher ─────┤                      │                    │
    └── Custom Agents ────┘                      ├─ Cache Manager    ├─ Notifications Groupées
                                                 ├─ Metrics Collector├─ Templates Multilingues
                                                 ├─ Config Manager   └─ Callbacks Avancés
                                                 └─ Web Interface
```

## Critères de Réussite Globaux

### Phase 1.5 (Migration Architecture - Immédiat)
- **Rétrocompatibilité :** Agents existants continuent de fonctionner
- **Performance :** < 100ms latence Publish → Toast affiché
- **Concurrence :** Support 20+ agents simultanés sans dégradation
- **Robustesse :** Reconnexion automatique en cas de coupure

### Phase 2 (Intégration SAM)
- **Migration :** Tous les agents SAM utilisent la nouvelle API
- **Fonctionnalités :** Support complet des 4 types de notifications
- **Performance :** Latence maintenue avec 50+ agents
- **Fiabilité :** 99.9% de succès des notifications en production

### Phase 3 (Améliorations Avancées)
- **Scalabilité :** Support 100+ agents avec monitoring temps réel
- **Extensibilité :** Nouvelles fonctionnalités sans impact sur l'existant
- **Maintenabilité :** Architecture modulaire avec tests complets
- **Observabilité :** Métriques et logs pour optimisation continue

## Maintenance et Support

### Maintenance Continue
- Mise à jour des dépendances Python
- Compatibilité avec nouvelles versions Windows
- Correction de bugs identifiés

### Support Écosystème SAM
- Assistance à l'intégration pour nouveaux agents
- Évolution de l'API selon besoins SAM
- Documentation maintenue à jour