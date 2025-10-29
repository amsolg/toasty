# DECISIONS - Log des Décisions Architecturales

## Vue d'Ensemble
Ce fichier trace chronologiquement toutes les décisions architecturales importantes prises pour Toasty.

## Log des Décisions

### 2025-10-27 - Choix du Protocole de Communication gRPC
**Contexte :** Besoin d'un protocole de communication efficace pour les notifications cross-platform et multi-langages
**Décision :** Utilisation de gRPC comme protocole de communication principal
**Raison :**
- Support natif multi-langages (Python, Node.js, Go, C#, etc.)
- Performance supérieure aux API REST
- Contrats stricts via Protocol Buffers
- Idéal pour communication agent-to-service dans l'écosystème SAM
**Impact :** Architecture orientée microservices, facilite l'intégration avec divers agents

### 2025-10-27 - Sélection de windows-toasts pour Notifications Windows
**Contexte :** Besoin d'afficher des notifications natives Windows 10/11
**Décision :** Utilisation de la bibliothèque `windows-toasts` plutôt que `plyer`
**Raison :**
- Notifications 100% natives Windows (pas d'émulation)
- Support complet des fonctionnalités Windows Toast (icônes, sons, Action Center)
- Meilleure intégration système
- Performance supérieure
**Impact :** Limitation à Windows uniquement, mais qualité notification optimale

### 2025-10-27 - Port Fixe 50053
**Contexte :** Choix du port d'écoute pour le serveur gRPC
**Décision :** Port fixe 50053 sur localhost uniquement
**Raison :**
- Évite les conflits avec ports standards (50051, 50052 souvent utilisés)
- Sécurité renforcée (localhost seulement)
- Simplicité de configuration pour l'écosystème SAM
**Impact :** Configuration simple, sécurité maximale, potentielle limitation multi-instance

### 2025-10-27 - Architecture Fire-and-Forget
**Contexte :** Définition du comportement de l'API de notification
**Décision :** Implémentation d'un modèle "fire-and-forget" avec confirmation de réception
**Raison :**
- Notifications ne doivent pas bloquer le workflow des agents
- Confirmation de réception suffisante pour validation
- Performance optimale pour les agents appelants
**Impact :** API simple, performance élevée, pas de tracking des interactions utilisateur

### 2025-10-27 - Structure Modulaire src/
**Contexte :** Organisation du code source du serveur
**Décision :** Séparation en modules `server.py` et `notification_logic.py`
**Raison :**
- Séparation des responsabilités (serveur gRPC vs logique métier)
- Facilite les tests unitaires
- Évolutivité pour futures fonctionnalités
**Impact :** Code maintenable, testable, extensible

### 2025-10-27 - Trois Niveaux de Notification
**Contexte :** Définition des types de notifications supportées
**Décision :** Support de 3 niveaux : INFO (0), WARNING (1), ERROR (2)
**Raison :**
- Couvre les besoins principaux des agents
- Mapping naturel avec icônes et sons Windows
- Simplicité d'utilisation
**Impact :** API claire, notifications visuellement distinctives

### 2025-10-28 - Génération Automatique Documentation Utilisateur
**Contexte :** Besoin de documentation complète pour adoption
**Décision :** Création de README.md et USAGE_GUIDE.md détaillés avec exemples multi-langages
**Raison :**
- Faciliter l'adoption par les développeurs
- Réduire les questions de support
- Démontrer les capacités du service
**Impact :** Adoption facilitée, intégration accélérée

### 2025-10-29 - Migration vers Structure SAM Standard
**Contexte :** Conformité aux standards de l'écosystème SAM
**Décision :** Restructuration complète de la documentation selon les standards SAM
**Raison :**
- Cohérence avec l'écosystème SAM
- Facilite la maintenance et la continuité
- Améliore la collaboration et le développement
**Impact :**
- CLAUDE.md converti en format d'héritage concis
- Contenu technique déplacé vers ARCHITECTURE.md
- Ajout de STATUS.md, ROADMAP.md, DECISIONS.md (ce fichier)
- Conformité 100% aux standards SAM

## Template pour Nouvelles Décisions

### [DATE] - [TITRE DE LA DÉCISION]
**Contexte :** [Description du problème ou besoin]
**Décision :** [Décision prise]
**Raison :** [Justification détaillée]
**Impact :** [Conséquences prévues sur l'architecture, performance, maintenance]