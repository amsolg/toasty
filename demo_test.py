#!/usr/bin/env python3
"""
Demonstration complete du systeme toasty
"""

import grpc
import sys
import os
import time

# Ajouter le répertoire gen au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'gen'))

import notifier_pb2
import notifier_pb2_grpc

def send_notification(title, message, level=0):
    """Envoie une notification"""
    try:
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = notifier_pb2_grpc.NotifierStub(channel)
            request = notifier_pb2.NotificationRequest(
                title=title,
                message=message,
                level=level
            )
            response = stub.SendNotification(request)

            level_names = {0: "INFO", 1: "WARNING", 2: "ERROR"}
            level_name = level_names.get(level, "UNKNOWN")

            if response.success:
                print(f"[{level_name}] '{title}' - SUCCESS")
            else:
                print(f"[{level_name}] '{title}' - ERREUR: {response.error_message}")

            return response.success
    except Exception as e:
        print(f"ERREUR DE CONNEXION: {e}")
        return False

def main():
    """Demo complete"""
    print("DEMONSTRATION TOASTY")
    print("=" * 50)

    # Test 1: Notification d'information
    print("\n1. Test notification INFO...")
    send_notification(
        "Information",
        "Ceci est une notification d'information basique",
        0
    )
    time.sleep(2)

    # Test 2: Notification d'avertissement
    print("\n2. Test notification WARNING...")
    send_notification(
        "Avertissement",
        "Attention ! Ceci est un message d'avertissement",
        1
    )
    time.sleep(2)

    # Test 3: Notification d'erreur
    print("\n3. Test notification ERROR...")
    send_notification(
        "Erreur Critique",
        "Une erreur critique s'est produite dans le systeme",
        2
    )
    time.sleep(2)

    # Test 4: Notification personnalisee
    print("\n4. Test notification personnalisee...")
    send_notification(
        "Agent Local",
        "Nouveau message recu de l'agent principal",
        0
    )

    print("\n" + "=" * 50)
    print("DEMO TERMINEE - Verifiez vos notifications Windows !")

if __name__ == '__main__':
    main()