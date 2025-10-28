"""
Logique de notification pour toasty utilisant windows-toasts
"""

from windows_toasts import WindowsToaster, Toast, ToastDisplayImage
import logging

class NotificationManager:
    """Gestionnaire des notifications Windows natives"""

    def __init__(self):
        """Initialise le gestionnaire de notifications"""
        self.toaster = WindowsToaster('Toasty')
        self.logger = logging.getLogger(__name__)

    def send_notification(self, title: str, message: str, level: int = 0) -> tuple[bool, str]:
        """
        Envoie une notification Windows native

        Args:
            title: Titre de la notification
            message: Contenu de la notification
            level: Niveau de priorité (0=INFO, 1=WARNING, 2=ERROR)

        Returns:
            tuple: (success: bool, error_message: str)
        """
        try:
            # Créer le toast
            toast = Toast()
            toast.text_fields = [title, message]

            # Définir l'icône selon le niveau
            if level == 1:  # WARNING
                # Icône d'avertissement (optionnel, Windows gère automatiquement)
                pass
            elif level == 2:  # ERROR
                # Icône d'erreur (optionnel, Windows gère automatiquement)
                pass
            # INFO par défaut

            # Envoyer la notification
            self.toaster.show_toast(toast)

            self.logger.info(f"Notification envoyée: {title} - {message}")
            return True, ""

        except Exception as e:
            error_msg = f"Erreur lors de l'envoi de la notification: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

def create_notification_manager() -> NotificationManager:
    """Factory function pour créer un gestionnaire de notifications"""
    return NotificationManager()