# Toasty 🐉🔥

**Service de notification de bureau unifié pour écosystèmes d'agents locaux**

Toasty est un serveur gRPC autonome qui permet à n'importe quelle application de créer des notifications Windows natives via une API simple et unifiée.

## ✨ Fonctionnalités

- 🪟 **Notifications Windows natives** - Toast notifications intégrées Windows 10/11
- 🔌 **API gRPC universelle** - Compatible avec tous les langages supportant gRPC
- 🎚️ **Trois niveaux de priorité** - INFO, WARNING, ERROR avec icônes appropriées
- 🛡️ **Sécurisé** - Écoute uniquement sur localhost
- ⚡ **Léger et rapide** - Empreinte mémoire minimale
- 🤖 **Agnostique** - Aucune connaissance du client requis

## 🚀 Démarrage Rapide

### Installation

```bash
git clone https://github.com/amsolg/toasty.git
cd toasty
pip install -r requirements.txt
```

### Démarrage du serveur

```bash
python run_server.py
```

### Test

```bash
python quick_test.py
```

## 📖 Utilisation

### Connexion basique

- **Adresse :** `localhost:50053`
- **Service :** `toasty.Notifier`
- **Méthode :** `SendNotification`

### Exemple Python

```python
import grpc
import notifier_pb2_grpc, notifier_pb2

# Connexion
with grpc.insecure_channel('localhost:50053') as channel:
    stub = notifier_pb2_grpc.NotifierStub(channel)

    # Notification
    request = notifier_pb2.NotificationRequest(
        title="Hello Toasty",
        message="Votre première notification !",
        level=0  # INFO
    )

    response = stub.SendNotification(request)
    print("Succès!" if response.success else f"Erreur: {response.error_message}")
```

## 📚 Documentation Complète

**➡️ [Guide d'Utilisation Détaillé](USAGE_GUIDE.md)**

Le guide complet inclut :
- Exemples pour Python, Node.js, Go, C#
- Gestion d'erreurs avancée
- Troubleshooting
- API complète
- Bonnes pratiques

## 🛠️ Architecture

```
Client App ──gRPC──► Toasty Server ──► Windows Toast API
    │                      │
    │                      ├─ Validation
    │                      ├─ Logging
    │                      └─ Error Handling
    │
    └─ Python/Node.js/Go/C#/...
```

## 📋 API

### NotificationRequest

| Champ | Type | Description |
|-------|------|-------------|
| `title` | string | Titre de la notification (requis) |
| `message` | string | Contenu de la notification (requis) |
| `level` | enum | Niveau: 0=INFO, 1=WARNING, 2=ERROR |

### NotificationResponse

| Champ | Type | Description |
|-------|------|-------------|
| `success` | bool | Succès de l'opération |
| `error_message` | string | Message d'erreur si échec |

## 🔧 Prérequis

- Windows 10/11
- Python 3.8+
- Packages : `grpcio`, `grpcio-tools`, `windows-toasts`

## 📁 Structure du Projet

```
toasty/
├── proto/notifier.proto          # Définition gRPC
├── src/
│   ├── server.py                 # Serveur gRPC principal
│   └── notification_logic.py     # Logique de notification
├── run_server.py                 # Script de démarrage
├── test_client.py                # Client de test complet
├── quick_test.py                 # Test rapide
├── demo_test.py                  # Démonstration
├── USAGE_GUIDE.md               # Documentation détaillée
└── requirements.txt              # Dépendances
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez les [issues](https://github.com/amsolg/toasty/issues) pour voir les améliorations en cours.

## 📄 Licence

Projet open source - voir les détails dans le repository.

---

**Créé pour simplifier les notifications desktop dans vos écosystèmes d'agents** 🤖