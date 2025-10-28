"""
Serveur gRPC pour toasty - Service de notification Windows
"""

import grpc
from concurrent import futures
import logging
import sys
import os

# Ajouter le répertoire gen au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'gen'))

import notifier_pb2
import notifier_pb2_grpc
from notification_logic import create_notification_manager

class NotifierService(notifier_pb2_grpc.NotifierServicer):
    """Implémentation du service gRPC Notifier"""

    def __init__(self):
        """Initialise le service avec le gestionnaire de notifications"""
        self.notification_manager = create_notification_manager()
        self.logger = logging.getLogger(__name__)

    def SendNotification(self, request, context):
        """
        Implémente l'appel RPC SendNotification

        Args:
            request: NotificationRequest avec title, message et level
            context: Contexte gRPC

        Returns:
            NotificationResponse avec success et error_message
        """
        self.logger.info(f"Notification reçue: '{request.title}' - '{request.message}' (niveau: {request.level})")

        # Valider la requête
        if not request.title.strip():
            error_msg = "Le titre de la notification ne peut pas être vide"
            self.logger.warning(error_msg)
            return notifier_pb2.NotificationResponse(
                success=False,
                error_message=error_msg
            )

        if not request.message.strip():
            error_msg = "Le message de la notification ne peut pas être vide"
            self.logger.warning(error_msg)
            return notifier_pb2.NotificationResponse(
                success=False,
                error_message=error_msg
            )

        # Envoyer la notification
        success, error_message = self.notification_manager.send_notification(
            title=request.title,
            message=request.message,
            level=request.level
        )

        return notifier_pb2.NotificationResponse(
            success=success,
            error_message=error_message
        )

def serve():
    """
    Démarre le serveur gRPC sur localhost:50053
    """
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Créer le serveur gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Ajouter le service
    notifier_pb2_grpc.add_NotifierServicer_to_server(NotifierService(), server)

    # Écouter sur localhost:50053
    listen_addr = 'localhost:50053'
    server.add_insecure_port(listen_addr)

    # Démarrer le serveur
    server.start()
    logger.info(f"Serveur toasty demarre sur {listen_addr}")
    logger.info("Appuyez sur Ctrl+C pour arreter le serveur")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Arrêt du serveur demandé...")
        server.stop(0)
        logger.info("Serveur arrêté")

if __name__ == '__main__':
    serve()