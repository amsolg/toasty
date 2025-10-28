# 📖 Guide d'Utilisation Toasty

**Toasty** 🐉🔥 est un service de notification de bureau unifié qui permet à n'importe quelle application de créer des notifications Windows natives via gRPC.

## 📋 Table des Matières

1. [Installation et Démarrage](#installation-et-démarrage)
2. [Connexion Basique](#connexion-basique)
3. [Format des Messages](#format-des-messages)
4. [Exemples par Langage](#exemples-par-langage)
5. [Niveaux de Notification](#niveaux-de-notification)
6. [Gestion d'Erreurs](#gestion-derreurs)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation et Démarrage

### Prérequis
- Windows 10/11
- Python 3.8+
- Les dépendances du projet installées

### Démarrage du Serveur

1. **Cloner le repository :**
   ```bash
   git clone https://github.com/amsolg/toasty.git
   cd toasty
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Démarrer le serveur :**
   ```bash
   python run_server.py
   ```

4. **Vérifier que le serveur fonctionne :**
   ```bash
   python quick_test.py
   ```

Le serveur sera accessible sur `localhost:50053`.

---

## 🔌 Connexion Basique

### Informations de Connexion

- **Adresse :** `localhost:50053`
- **Protocole :** gRPC (HTTP/2)
- **Sécurité :** Connexion non-sécurisée (localhost uniquement)
- **Service :** `toasty.Notifier`
- **Méthode :** `SendNotification`

### Architecture du Message

```protobuf
service Notifier {
  rpc SendNotification (NotificationRequest) returns (NotificationResponse);
}

message NotificationRequest {
  string title = 1;     // Titre de la notification (requis)
  string message = 2;   // Corps du message (requis)
  Level level = 3;      // Niveau de priorité (optionnel, défaut: INFO)
}

message NotificationResponse {
  bool success = 1;         // Succès de l'opération
  string error_message = 2; // Message d'erreur si échec
}
```

---

## 📝 Format des Messages

### Champs Requis

| Champ | Type | Description | Exemple |
|-------|------|-------------|---------|
| `title` | string | Titre de la notification | "Nouveau Message" |
| `message` | string | Contenu de la notification | "Vous avez reçu un email" |

### Champs Optionnels

| Champ | Type | Description | Valeurs |
|-------|------|-------------|---------|
| `level` | enum | Niveau de priorité | `0` (INFO), `1` (WARNING), `2` (ERROR) |

---

## 💻 Exemples par Langage

### Python

#### Installation
```bash
pip install grpcio grpcio-tools
```

#### Code
```python
import grpc
import sys
import os

# Ajouter le path vers les stubs générés
sys.path.append('path/to/toasty/gen')
import notifier_pb2
import notifier_pb2_grpc

def send_notification(title, message, level=0):
    """Envoie une notification via Toasty"""
    try:
        # Connexion au serveur
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = notifier_pb2_grpc.NotifierStub(channel)

            # Créer la requête
            request = notifier_pb2.NotificationRequest(
                title=title,
                message=message,
                level=level
            )

            # Envoyer la notification
            response = stub.SendNotification(request)

            if response.success:
                print("Notification envoyée avec succès!")
                return True
            else:
                print(f"Erreur: {response.error_message}")
                return False

    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return False

# Utilisation
send_notification("Test", "Message de test", 0)
```

### Node.js

#### Installation
```bash
npm install @grpc/grpc-js @grpc/proto-loader
```

#### Code
```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// Charger le fichier proto
const PROTO_PATH = path.join(__dirname, 'proto/notifier.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH);
const toasty = grpc.loadPackageDefinition(packageDefinition).toasty;

// Créer le client
const client = new toasty.Notifier('localhost:50053',
    grpc.credentials.createInsecure());

function sendNotification(title, message, level = 0) {
    return new Promise((resolve, reject) => {
        const request = {
            title: title,
            message: message,
            level: level
        };

        client.SendNotification(request, (error, response) => {
            if (error) {
                reject(error);
            } else if (response.success) {
                console.log('Notification envoyée avec succès!');
                resolve(true);
            } else {
                console.log(`Erreur: ${response.error_message}`);
                resolve(false);
            }
        });
    });
}

// Utilisation
sendNotification("Test Node.js", "Message depuis Node.js")
    .then(success => console.log('Résultat:', success))
    .catch(error => console.error('Erreur:', error));
```

### Go

#### Installation
```bash
go mod init your-app
go get google.golang.org/grpc
go get google.golang.org/protobuf/cmd/protoc-gen-go
go get google.golang.org/grpc/cmd/protoc-gen-go-grpc
```

#### Code
```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"

    // Importer vos stubs générés
    pb "your-app/gen"
)

func sendNotification(title, message string, level int32) error {
    // Connexion au serveur
    conn, err := grpc.Dial("localhost:50053",
        grpc.WithTransportCredentials(insecure.NewCredentials()))
    if err != nil {
        return fmt.Errorf("connexion échouée: %v", err)
    }
    defer conn.Close()

    // Créer le client
    client := pb.NewNotifierClient(conn)

    // Préparer la requête
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    request := &pb.NotificationRequest{
        Title:   title,
        Message: message,
        Level:   pb.NotificationRequest_Level(level),
    }

    // Envoyer la notification
    response, err := client.SendNotification(ctx, request)
    if err != nil {
        return fmt.Errorf("erreur RPC: %v", err)
    }

    if response.Success {
        fmt.Println("Notification envoyée avec succès!")
        return nil
    } else {
        return fmt.Errorf("erreur du serveur: %s", response.ErrorMessage)
    }
}

func main() {
    err := sendNotification("Test Go", "Message depuis Go", 0)
    if err != nil {
        log.Fatal(err)
    }
}
```

### C# (.NET)

#### Installation
```bash
dotnet add package Grpc.Net.Client
dotnet add package Google.Protobuf
dotnet add package Grpc.Tools
```

#### Code
```csharp
using Grpc.Net.Client;
using System;
using System.Threading.Tasks;

// Générer les stubs depuis le .proto avec Grpc.Tools
using Toasty;

class Program
{
    static async Task Main(string[] args)
    {
        await SendNotificationAsync("Test C#", "Message depuis C#", 0);
    }

    static async Task<bool> SendNotificationAsync(string title, string message, int level = 0)
    {
        try
        {
            // Créer le channel
            using var channel = GrpcChannel.ForAddress("http://localhost:50053");
            var client = new Notifier.NotifierClient(channel);

            // Créer la requête
            var request = new NotificationRequest
            {
                Title = title,
                Message = message,
                Level = (NotificationRequest.Types.Level)level
            };

            // Envoyer la notification
            var response = await client.SendNotificationAsync(request);

            if (response.Success)
            {
                Console.WriteLine("Notification envoyée avec succès!");
                return true;
            }
            else
            {
                Console.WriteLine($"Erreur: {response.ErrorMessage}");
                return false;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Erreur de connexion: {ex.Message}");
            return false;
        }
    }
}
```

---

## 🎚️ Niveaux de Notification

### Niveaux Disponibles

| Niveau | Valeur | Description | Icône Windows |
|--------|--------|-------------|---------------|
| **INFO** | `0` | Information générale | ℹ️ Information |
| **WARNING** | `1` | Avertissement | ⚠️ Attention |
| **ERROR** | `2` | Erreur critique | ❌ Erreur |

### Exemples d'Usage

```python
# Notification d'information
send_notification("Tâche Terminée", "Le backup est terminé", 0)

# Notification d'avertissement
send_notification("Espace Disque", "Espace disque faible", 1)

# Notification d'erreur
send_notification("Erreur Critique", "Échec de connexion à la base", 2)
```

---

## ⚠️ Gestion d'Erreurs

### Types d'Erreurs Possibles

1. **Erreurs de connexion**
   - Serveur non démarré
   - Port bloqué
   - Problème réseau

2. **Erreurs de validation**
   - Titre vide
   - Message vide
   - Niveau invalide

3. **Erreurs système**
   - Problème avec windows-toasts
   - Permissions insuffisantes

### Exemple de Gestion Robuste

```python
def send_notification_safe(title, message, level=0, retries=3):
    """Envoie une notification avec gestion d'erreurs et retry"""

    # Validation locale
    if not title.strip():
        raise ValueError("Le titre ne peut pas être vide")
    if not message.strip():
        raise ValueError("Le message ne peut pas être vide")
    if level not in [0, 1, 2]:
        raise ValueError("Le niveau doit être 0, 1 ou 2")

    for attempt in range(retries):
        try:
            with grpc.insecure_channel('localhost:50053') as channel:
                stub = notifier_pb2_grpc.NotifierStub(channel)
                request = notifier_pb2.NotificationRequest(
                    title=title, message=message, level=level
                )
                response = stub.SendNotification(request)

                if response.success:
                    return True
                else:
                    print(f"Erreur serveur: {response.error_message}")
                    return False

        except grpc.RpcError as e:
            print(f"Tentative {attempt + 1}/{retries} échouée: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(1)  # Attendre avant retry
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            raise

    return False
```

---

## 🔧 Troubleshooting

### Problèmes Courants

#### 1. "Connection refused" / "Connexion refusée"

**Cause :** Le serveur Toasty n'est pas démarré

**Solution :**
```bash
# Vérifier si le serveur tourne
netstat -an | findstr :50053

# Redémarrer le serveur
python run_server.py
```

#### 2. "Module not found" pour les stubs gRPC

**Cause :** Les stubs gRPC ne sont pas générés ou pas dans le path

**Solution :**
```bash
# Regénérer les stubs
python -m grpc_tools.protoc --proto_path=proto --python_out=gen --grpc_python_out=gen proto/notifier.proto

# Vérifier que les fichiers existent
ls gen/notifier_pb2*.py
```

#### 3. Les notifications n'apparaissent pas

**Causes possibles :**
- Mode "Ne pas déranger" activé
- Notifications désactivées pour Python
- Problème de permissions

**Solutions :**
```bash
# Tester avec le client de test
python quick_test.py

# Vérifier les paramètres Windows
# Paramètres > Système > Notifications et actions
```

#### 4. Erreur d'encodage des caractères

**Cause :** Problème d'encodage Windows avec les caractères spéciaux

**Solution :**
```python
# Encoder explicitement en UTF-8
title = "Título con acentos".encode('utf-8').decode('utf-8')
message = "Mensagem com caractères especiais"
```

### Tests de Diagnostic

#### Test de Connectivité
```python
import grpc

def test_connection():
    try:
        channel = grpc.insecure_channel('localhost:50053')
        grpc.channel_ready_future(channel).result(timeout=5)
        print("✅ Connexion au serveur OK")
        return True
    except grpc.FutureTimeoutError:
        print("❌ Timeout - Serveur non accessible")
        return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

test_connection()
```

#### Test Complet
```bash
# Utiliser le script de démo fourni
python demo_test.py
```

---

## 📞 Support

### Ressources

- **Repository GitHub :** [https://github.com/amsolg/toasty](https://github.com/amsolg/toasty)
- **Documentation :** Voir `CLAUDE.md` dans le repository
- **Issues :** Utiliser les GitHub Issues pour rapporter des bugs

### Contribution

Les contributions sont les bienvenues ! Voir le repository GitHub pour les guidelines de contribution.

---

**Toasty** 🐉🔥 - Service de notification unifié pour écosystèmes d'agents