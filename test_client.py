#!/usr/bin/env python3
"""
Client de test pour le serveur toasty
"""

import grpc
import sys
import os

# Ajouter le répertoire gen au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'gen'))

import notifier_pb2
import notifier_pb2_grpc

def test_notification(title: str, message: str, level: int = 0):
    """
    Envoie une notification de test au serveur toasty

    Args:
        title: Titre de la notification
        message: Message de la notification
        level: Niveau (0=INFO, 1=WARNING, 2=ERROR)
    """
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
            print(f"Envoi de la notification: '{title}' - '{message}' (niveau: {level})")
            response = stub.SendNotification(request)

            # Afficher le résultat
            if response.success:
                print("Notification envoyee avec succes!")
            else:
                print(f"Erreur: {response.error_message}")

    except grpc.RpcError as e:
        print(f"Erreur gRPC: {e}")
    except Exception as e:
        print(f"Erreur: {e}")

def main():
    """Fonction principale pour tester différents types de notifications"""
    print("Client de test toasty")
    print("=" * 40)

    # Test 1: Notification INFO
    test_notification(
        title="Test Info",
        message="Ceci est une notification d'information",
        level=0
    )
    input("Appuyez sur Entrée pour continuer...")

    # Test 2: Notification WARNING
    test_notification(
        title="Test Avertissement",
        message="Ceci est une notification d'avertissement",
        level=1
    )
    input("Appuyez sur Entrée pour continuer...")

    # Test 3: Notification ERROR
    test_notification(
        title="Test Erreur",
        message="Ceci est une notification d'erreur",
        level=2
    )
    input("Appuyez sur Entrée pour continuer...")

    # Test 4: Notification personnalisée
    title = input("Entrez un titre personnalisé: ").strip()
    message = input("Entrez un message personnalisé: ").strip()

    if title and message:
        test_notification(title, message, 0)
    else:
        print("Titre et message requis")

if __name__ == '__main__':
    main()