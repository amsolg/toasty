#!/usr/bin/env python3
"""
Test rapide d'une notification
"""

import grpc
import sys
import os

# Ajouter le répertoire gen au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'gen'))

import notifier_pb2
import notifier_pb2_grpc

def quick_test():
    """Test rapide d'une notification"""
    try:
        # Connexion au serveur
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = notifier_pb2_grpc.NotifierStub(channel)

            # Créer la requête
            request = notifier_pb2.NotificationRequest(
                title="Test toasty",
                message="Votre serveur de notification fonctionne parfaitement !",
                level=0
            )

            # Envoyer la notification
            print("Envoi d'une notification de test...")
            response = stub.SendNotification(request)

            # Afficher le résultat
            if response.success:
                print("SUCCESS: Notification envoyee ! Verifiez votre bureau.")
                return True
            else:
                print(f"ERREUR: {response.error_message}")
                return False

    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == '__main__':
    quick_test()