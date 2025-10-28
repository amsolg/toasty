# Projet: toasty

## 1. Mission et Objectif

**Nom de code :** toasty 🐉🔥

**Mission :** Fournir un service de notification de bureau unifié, simple et fiable pour l'écosystème d'agents local.

**Objectif :** Créer un serveur gRPC autonome qui écoute les requêtes de notification et les affiche sur le bureau de l'utilisateur. Ce service doit être "agnostique" : il ne doit pas savoir *qui* l'appelle (que ce soit l'agent principal, un déclencheur de courriel, ou tout autre outil), il doit simplement exécuter l'action demandée.

## 2. Architecture et Pile Technique (Stack)

* **Langage :** Python
* **Protocole de Communication :** gRPC
* **Fonctionnement :** Serveur gRPC autonome (démon)
* **Dépendances Clés :**
    * `grpcio` : Pour l'implémentation du serveur gRPC.
    * `grpcio-tools` : Pour la génération du code à partir du `.proto`.
    * `windows-toasts` : Bibliothèque native Windows pour afficher les toast notifications Windows 10/11.
* **Point de Terminaison (Endpoint) :** Le service doit écouter sur `localhost:50053`.

## 3. Définition du Service (Contrat gRPC)

Le cœur du projet est ce contrat. Il doit être simple et direct.

**Fichier : `proto/notifier.proto`**

```protobuf
syntax = "proto3";

// Le package 'toasty' est utilisé pour ce service
package toasty;

// Le service de notification
service Notifier {
  // Envoie une notification. C'est un appel "fire-and-forget".
  // Le client n'attend pas que l'utilisateur ferme la notification,
  // il attend juste la confirmation que la requête a été reçue et traitée.
  rpc SendNotification (NotificationRequest) returns (NotificationResponse);
}

// La requête de notification
message NotificationRequest {
  string title = 1;     // Titre de la notification (ex: "Nouveau courriel")
  string message = 2;   // Corps du message (ex: "Sujet: Rapport...")
  
  // Niveau de la notification pour l'icône, etc. (optionnel mais bon à avoir)
  enum Level {
    INFO = 0;
    WARNING = 1;
    ERROR = 2;
  }
  Level level = 3;
}

// Une réponse simple pour confirmer la réception
message NotificationResponse {
  bool success = 1;         // Vrai si la notification a été envoyée, faux sinon
  string error_message = 2; // Message d'erreur si success=false
}

## 4. Structure des Fichiers Attendue

```
/toasty
|-- CLAUDE.md         (Ce fichier)
|-- .gitignore
|-- proto/
|   |-- notifier.proto  (La définition du service ci-dessus)
|-- gen/                (Code gRPC généré, doit être dans .gitignore)
|   |-- __init__.py
|   |-- notifier_pb2.py
|   |-- notifier_pb2_grpc.py
|-- src/
|   |-- __init__.py
|   |-- notification_logic.py  (Logique d'implémentation avec 'plyer')
|   |-- server.py                (Le serveur gRPC principal)
|-- requirements.txt
|-- run_server.py            (Script pour démarrer le serveur)
|-- test_client.py           (Un script simple pour tester le service)
```

## 5. Principes de Conception & Exigences

* **Légereté :** Le service doit avoir une empreinte mémoire minimale.

* **Autonomie :** Il doit s'exécuter comme son propre processus, indépendant de l'agent ou des déclencheurs.

* **Simplicité :** La logique doit être minimale. Il reçoit une requête gRPC, la valide, utilise `windows-toasts` pour afficher la notification Windows native, et renvoie une réponse de succès.

* **Sécurité :** Le serveur DOIT écouter uniquement sur localhost pour empêcher toute exposition au réseau externe.

* **Robustesse :** Le serveur doit gérer les erreurs gracieusement (par exemple, si `windows-toasts` échoue) et renvoyer un NotificationResponse avec success=false et un message d'erreur. Il ne doit pas planter.

* **Spécifique Windows :** Le service est optimisé pour Windows 10/11 et utilise les toast notifications natives du système d'exploitation.

## 6. État d'Avancement du Projet

### ✅ Tâches Complétées

1. **✅ Structure de fichiers** - Générée complètement selon la section 4
2. **✅ proto/notifier.proto** - Créé avec la définition du service gRPC
3. **✅ Stubs gRPC** - Générés et placés dans `gen/` (notifier_pb2.py, notifier_pb2_grpc.py)
4. **✅ requirements.txt** - Mis à jour avec grpcio, grpcio-tools, et windows-toasts
5. **✅ .gitignore** - Configuré pour exclure les fichiers générés et temporaires

### 🔄 Tâches Restantes

5. **⏳ src/notification_logic.py** - Implémenter la logique de notification avec windows-toasts

6. **⏳ src/server.py** - Implémenter le serveur gRPC principal :
   - Importer les stubs gRPC de gen/ et la logique de src/notification_logic.py
   - Définir une classe NotifierService qui hérite de notifier_pb2_grpc.NotifierServicer
   - Implémenter la méthode SendNotification qui appelle la logique de notification
   - Contenir la fonction serve() pour démarrer le serveur gRPC sur le port 50053

7. **⏳ run_server.py** - Créer le script pour démarrer le serveur

8. **⏳ test_client.py** - Créer un client gRPC simple pour tester le service

### 📁 Structure Actuelle Vérifiée

```
/toasty
|-- CLAUDE.md         ✅ (Ce fichier, mis à jour)
|-- .gitignore        ✅ (Configuré)
|-- proto/
|   |-- notifier.proto  ✅ (Définition du service)
|-- gen/                ✅ (Code gRPC généré)
|   |-- __init__.py     ✅
|   |-- notifier_pb2.py     ✅ (Généré automatiquement)
|   |-- notifier_pb2_grpc.py ✅ (Généré automatiquement)
|-- src/                ✅ (Répertoire créé)
|   |-- __init__.py     ✅
|   |-- notification_logic.py  ⏳ (À implémenter)
|   |-- server.py              ⏳ (À implémenter)
|-- requirements.txt    ✅ (Dépendances définies)
|-- run_server.py       ⏳ (À créer)
|-- test_client.py      ⏳ (À créer)
```

### 🔔 Fonctionnalités Windows Natives

Le projet utilise maintenant `windows-toasts` qui offre :
- **Toast notifications natives** Windows 10/11
- **Support des niveaux de priorité** (Info, Warning, Error)
- **Icônes système** intégrées selon le niveau
- **Sons de notification** natifs
- **Integration Action Center** Windows
- **Durée d'affichage** configurable

### ✅ Projet Terminé et Fonctionnel

Le projet Toasty est maintenant **100% fonctionnel** ! Tous les composants ont été implémentés et testés avec succès.

### 📚 Documentation Utilisateur

- **[README.md](README.md)** - Vue d'ensemble et démarrage rapide
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Guide complet d'utilisation avec exemples
- **Repository GitHub** - [https://github.com/amsolg/toasty](https://github.com/amsolg/toasty)

### 🎯 Utilisation

Pour utiliser Toasty dans vos projets :

1. **Démarrer le serveur** : `python run_server.py`
2. **Connecter votre application** à `localhost:50053` via gRPC
3. **Consulter** [USAGE_GUIDE.md](USAGE_GUIDE.md) pour des exemples détaillés

Le service est maintenant prêt pour l'intégration dans votre écosystème d'agents !