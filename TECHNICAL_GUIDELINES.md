# TECHNICAL GUIDELINES - Toasty

## Vue d'Ensemble
Ce document détaille les patterns de code, bonnes pratiques et exemples d'implémentation pour le service de notification Toasty, basé sur les recommandations expertes pour Python, gRPC et Windows Toast.

## 1. Architecture asyncio + grpc.aio

### Justification Technique
Le choix d'asyncio pour un serveur gRPC I/O-bound est **critique** pour les performances :
- **GIL Python :** Évite la compétition entre threads
- **Mémoire :** Gestion de milliers de connexions dormantes avec empreinte minimale
- **Latence :** Élimination de la surcharge de commutation de contexte

### Pattern de Base - Serveur Asyncio

```python
import asyncio
import signal
from typing import Dict, Set
import grpc
from grpc import aio
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2_grpc

class AsyncNotificationServer:
    def __init__(self):
        self.server = None
        self.health_servicer = health.HealthServicer()
        self.subscriber_manager = AsyncSubscriberManager()

    async def start_server(self, port: int = 50053):
        """Démarre le serveur gRPC asyncio avec health checks"""
        self.server = aio.server()

        # Ajouter les services
        notifications_pb2_grpc.add_NotificationServiceServicer_to_server(
            NotificationServicer(self.subscriber_manager), self.server
        )
        health_pb2_grpc.add_HealthServicer_to_server(
            self.health_servicer, self.server
        )

        # Configurer l'écoute
        listen_addr = f'localhost:{port}'
        self.server.add_insecure_port(listen_addr)

        # Marquer comme healthy
        self.health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

        await self.server.start()
        print(f"🚀 Serveur démarré sur {listen_addr}")

        # Configuration graceful shutdown
        self._setup_signal_handlers()

        await self.server.wait_for_termination()

    def _setup_signal_handlers(self):
        """Configure les handlers pour arrêt gracieux"""
        def signal_handler(signum, frame):
            print(f"📡 Signal {signum} reçu, arrêt gracieux...")
            asyncio.create_task(self.graceful_shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def graceful_shutdown(self, grace_period: int = 5):
        """Séquence d'arrêt gracieux recommandée"""
        # 1. Marquer comme NOT_SERVING
        self.health_servicer.set("", health_pb2.HealthCheckResponse.NOT_SERVING)

        # 2. Arrêter le serveur avec période de grâce
        await self.server.stop(grace_period)

        # 3. Cleanup des ressources
        await self.subscriber_manager.cleanup()

        print("✅ Arrêt gracieux terminé")
```

### Contrainte Critique : Pas de Code Bloquant
```python
# ❌ INTERDIT - Bloque la boucle d'événements
def bad_toast_render(notification):
    time.sleep(0.1)  # BLOQUE TOUT LE SERVEUR
    toaster.show_toast(toast)

# ✅ CORRECT - Délégation vers executor
async def good_toast_render(notification):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,  # ThreadPoolExecutor par défaut
        _render_toast_sync,
        notification
    )

def _render_toast_sync(notification):
    """Fonction synchrone isolée pour rendu toast"""
    toaster = WindowsToaster("Toasty")
    toast = _build_toast_from_protobuf(notification)
    toaster.show_toast(toast)
```

## 2. Gestion des Abonnés Asynchrone

### AsyncSubscriberManager Pattern

```python
import asyncio
from typing import Dict
from contextlib import asynccontextmanager

class AsyncSubscriberManager:
    def __init__(self):
        self._subscribers: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def add_subscriber(self, client_id: str) -> asyncio.Queue:
        """Ajoute un abonné avec file d'attente dédiée"""
        async with self._lock:
            if client_id in self._subscribers:
                print(f"⚠️ Client {client_id} déjà connecté, remplacement")

            message_queue = asyncio.Queue(maxsize=100)  # Limite pour éviter memory leak
            self._subscribers[client_id] = message_queue
            print(f"✅ Abonné ajouté : {client_id}")
            return message_queue

    async def remove_subscriber(self, client_id: str):
        """Supprime un abonné et nettoie ses ressources"""
        async with self._lock:
            if client_id in self._subscribers:
                queue = self._subscribers.pop(client_id)
                # Vider la queue pour libérer la mémoire
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                print(f"🗑️ Abonné supprimé : {client_id}")

    async def publish_to_client(self, client_id: str, notification) -> bool:
        """Publie une notification vers un client spécifique"""
        async with self._lock:
            if client_id not in self._subscribers:
                return False

            try:
                # Non-bloquant avec timeout pour éviter blocage
                self._subscribers[client_id].put_nowait(notification)
                return True
            except asyncio.QueueFull:
                print(f"⚠️ Queue pleine pour {client_id}, notification droppée")
                return False

    @asynccontextmanager
    async def subscribe_context(self, client_id: str):
        """Context manager pour gestion automatique lifecycle"""
        queue = await self.add_subscriber(client_id)
        try:
            yield queue
        finally:
            await self.remove_subscriber(client_id)

    async def cleanup(self):
        """Nettoyage complet pour shutdown"""
        async with self._lock:
            for client_id in list(self._subscribers.keys()):
                await self.remove_subscriber(client_id)
```

## 3. Service gRPC avec Patterns de Production

### NotificationServicer Asyncio

```python
import grpc
from grpc import aio
import notifications_pb2
import notifications_pb2_grpc

class NotificationServicer(notifications_pb2_grpc.NotificationServiceServicer):
    def __init__(self, subscriber_manager: AsyncSubscriberManager):
        self.subscriber_manager = subscriber_manager

    async def Subscribe(self, request, context):
        """RPC streaming pour abonnement client"""
        client_id = request.client_id

        # Utilisation du context manager pour cleanup automatique
        async with self.subscriber_manager.subscribe_context(client_id) as queue:
            # Configurer cleanup sur déconnexion
            context.add_callback(
                lambda: print(f"🔌 Client {client_id} déconnecté")
            )

            try:
                while context.is_active():
                    try:
                        # Attendre notification avec timeout pour vérifier connexion
                        notification = await asyncio.wait_for(
                            queue.get(),
                            timeout=1.0
                        )
                        yield notification

                    except asyncio.TimeoutError:
                        # Timeout normal, continuer la boucle
                        continue

            except grpc.RpcError as e:
                print(f"❌ Erreur RPC pour {client_id}: {e.details()}")
            except Exception as e:
                print(f"💥 Erreur inattendue pour {client_id}: {e}")

    async def Publish(self, request, context):
        """RPC unaire pour publication de notification"""
        target_id = request.target_client_id
        notification = request.notification

        try:
            # Validation business logic
            if not notification.id:
                notification.id = f"notif_{asyncio.get_event_loop().time()}"

            # Publication asynchrone
            success = await self.subscriber_manager.publish_to_client(
                target_id, notification
            )

            # Rendu toast asynchrone (délégué à executor)
            if success:
                await self._render_toast_async(notification)

            return notifications_pb2.PublishResponse(
                notification_id=notification.id,
                success=success
            )

        except Exception as e:
            # Mapping exception vers code gRPC approprié
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"Erreur lors de la publication: {str(e)}"
            )

    async def _render_toast_async(self, notification):
        """Rendu toast délégué vers thread executor"""
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                self._render_toast_sync,
                notification
            )
        except Exception as e:
            print(f"⚠️ Échec rendu toast: {e}")

    def _render_toast_sync(self, notification):
        """Fonction synchrone pour interaction avec windows-toasts"""
        from windows_toasts import WindowsToaster, Toast

        toaster = WindowsToaster("Toasty SAM")
        toast = Toast()

        # Mapping basé sur le type de payload (oneof)
        payload_type = notification.WhichOneof('payload')

        if payload_type == 'text_message':
            payload = notification.text_message
            toast.text_fields = [
                payload.header.title,
                payload.body_text_line1,
                payload.body_text_line2
            ]
        # ... autres types de payload

        # Configuration audio selon urgency
        if notification.urgency == notifications_pb2.UrgencyLevel.CRITICAL:
            toast.audio = 'ms-winsoundevent:Notification.Looping.Alarm'

        toaster.show_toast(toast)
```

## 4. Intercepteurs pour Préoccupations Transversales

### Rate Limiting Intercepteur

```python
import time
from typing import Dict
import grpc
from grpc import aio
from aiolimiter import AsyncLimiter

class RateLimitingInterceptor(aio.ServerInterceptor):
    def __init__(self, rate_limit: float = 10.0, per_seconds: float = 60.0):
        # Limiters par agent (basé sur x-agent-id)
        self._limiters: Dict[str, AsyncLimiter] = {}
        self._default_rate = rate_limit
        self._default_period = per_seconds

    def _get_agent_id(self, metadata) -> str:
        """Extrait l'ID agent des métadonnées gRPC"""
        for key, value in metadata:
            if key == 'x-agent-id':
                return value
        return 'unknown'

    def _get_limiter(self, agent_id: str) -> AsyncLimiter:
        """Récupère ou crée un limiter pour cet agent"""
        if agent_id not in self._limiters:
            self._limiters[agent_id] = AsyncLimiter(
                self._default_rate,
                self._default_period
            )
        return self._limiters[agent_id]

    async def intercept_service(self, continuation, handler_call_details):
        """Intercepte et applique rate limiting"""
        metadata = dict(handler_call_details.invocation_metadata)
        agent_id = self._get_agent_id(handler_call_details.invocation_metadata)

        limiter = self._get_limiter(agent_id)

        # Vérifier la limite
        if not await limiter.acquire():
            print(f"🚫 Rate limit dépassé pour agent {agent_id}")
            # Retourner une erreur RESOURCE_EXHAUSTED
            raise grpc.RpcError(grpc.StatusCode.RESOURCE_EXHAUSTED)

        # Continuer le traitement
        return await continuation(handler_call_details)
```

### Exception Mapping Intercepteur

```python
import grpc
from grpc import aio
import logging

class ExceptionMappingInterceptor(aio.ServerInterceptor):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def intercept_service(self, continuation, handler_call_details):
        """Mappe les exceptions Python vers codes gRPC appropriés"""
        try:
            return await continuation(handler_call_details)

        except ValueError as e:
            self.logger.warning(f"Validation error: {e}")
            raise grpc.RpcError(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except PermissionError as e:
            self.logger.warning(f"Permission denied: {e}")
            raise grpc.RpcError(grpc.StatusCode.PERMISSION_DENIED, str(e))

        except FileNotFoundError as e:
            self.logger.warning(f"Resource not found: {e}")
            raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, str(e))

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, "Erreur interne du serveur")
```

## 5. Client Pattern avec Reconnexion

### Client Resilient Pattern

```python
import asyncio
import grpc
from grpc import aio
import random

class ResilientNotificationClient:
    def __init__(self, server_address: str, client_id: str):
        self.server_address = server_address
        self.client_id = client_id
        self.channel = None
        self.stub = None
        self._reconnect_delay = 1.0
        self._max_reconnect_delay = 60.0

    async def connect(self):
        """Établit la connexion avec keepalives"""
        options = [
            ('grpc.keepalive_time_ms', 5 * 60 * 1000),  # 5 minutes
            ('grpc.keepalive_timeout_ms', 20 * 1000),   # 20 secondes
            ('grpc.keepalive_permit_without_calls', True),
        ]

        self.channel = aio.insecure_channel(self.server_address, options=options)
        self.stub = notifications_pb2_grpc.NotificationServiceStub(self.channel)

    async def subscribe_with_retry(self):
        """Boucle d'abonnement avec reconnexion automatique"""
        while True:
            try:
                await self.connect()

                request = notifications_pb2.SubscriptionRequest(client_id=self.client_id)

                print(f"🔗 Connexion pour client {self.client_id}")

                async for notification in self.stub.Subscribe(request):
                    await self._handle_notification(notification)
                    # Reset du délai de reconnexion en cas de succès
                    self._reconnect_delay = 1.0

            except grpc.RpcError as e:
                if e.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.CANCELLED):
                    print(f"🔄 Connexion perdue, reconnexion dans {self._reconnect_delay}s")
                    await asyncio.sleep(self._reconnect_delay)
                    # Backoff exponentiel avec jitter
                    self._reconnect_delay = min(
                        self._reconnect_delay * 2 + random.uniform(0, 1),
                        self._max_reconnect_delay
                    )
                else:
                    print(f"❌ Erreur gRPC non récupérable: {e}")
                    break

            except Exception as e:
                print(f"💥 Erreur inattendue: {e}")
                await asyncio.sleep(self._reconnect_delay)

    async def _handle_notification(self, notification):
        """Traite une notification reçue"""
        print(f"📬 Notification reçue: {notification.id}")
        # Traitement spécifique à l'agent
        pass

    async def close(self):
        """Ferme proprement la connexion"""
        if self.channel:
            await self.channel.close()
```

## 6. Configuration et Déploiement

### Configuration via Variables d'Environnement

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ToastyConfig:
    # Serveur
    host: str = "localhost"
    port: int = 50053

    # Rate Limiting
    rate_limit_per_agent: float = 10.0
    rate_limit_window_seconds: float = 60.0

    # Health & Monitoring
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    metrics_port: int = 9090

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Windows Specific
    aumid: str = "SAM.Toasty.NotificationService"

    @classmethod
    def from_env(cls) -> 'ToastyConfig':
        """Charge la configuration depuis l'environnement"""
        return cls(
            host=os.getenv('TOASTY_HOST', cls.host),
            port=int(os.getenv('TOASTY_PORT', cls.port)),
            rate_limit_per_agent=float(os.getenv('TOASTY_RATE_LIMIT', cls.rate_limit_per_agent)),
            rate_limit_window_seconds=float(os.getenv('TOASTY_RATE_WINDOW', cls.rate_limit_window_seconds)),
            health_check_enabled=os.getenv('TOASTY_HEALTH_ENABLED', 'true').lower() == 'true',
            metrics_enabled=os.getenv('TOASTY_METRICS_ENABLED', 'true').lower() == 'true',
            metrics_port=int(os.getenv('TOASTY_METRICS_PORT', cls.metrics_port)),
            log_level=os.getenv('TOASTY_LOG_LEVEL', cls.log_level),
            log_format=os.getenv('TOASTY_LOG_FORMAT', cls.log_format),
            aumid=os.getenv('TOASTY_AUMID', cls.aumid),
        )
```

### Script AUMID pour Déploiement

```python
import winreg
import sys
from pathlib import Path

def register_aumid(app_id: str, app_name: str, icon_path: Optional[str] = None):
    """
    Enregistre l'AUMID dans le registre Windows
    Nécessite des privilèges administrateur
    """
    try:
        # Clé de registre pour l'application
        key_path = f"SOFTWARE\\Classes\\AppUserModelId\\{app_id}"

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            # Nom affiché
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)

            # Icône si fournie
            if icon_path and Path(icon_path).exists():
                winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, icon_path)

        print(f"✅ AUMID {app_id} enregistré avec succès")
        return True

    except PermissionError:
        print("❌ Privilèges administrateur requis pour l'enregistrement AUMID")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement AUMID: {e}")
        return False

if __name__ == "__main__":
    # Configuration par défaut
    AUMID = "SAM.Toasty.NotificationService"
    APP_NAME = "Toasty - SAM Notification Service"

    success = register_aumid(AUMID, APP_NAME)
    sys.exit(0 if success else 1)
```

## 7. Tests et Validation

### Tests d'Intégration Asyncio

```python
import pytest
import asyncio
import grpc
from grpc import aio

@pytest.mark.asyncio
async def test_publish_subscribe_flow():
    """Test complet du flux Publish/Subscribe"""
    # Setup
    server = AsyncNotificationServer()
    await server.start_server_background()

    client = ResilientNotificationClient("localhost:50053", "test-agent")
    await client.connect()

    try:
        # Test de publication
        notification = notifications_pb2.Notification(
            id="test-001",
            urgency=notifications_pb2.UrgencyLevel.INFO,
            text_message=notifications_pb2.TextMessage(
                header=notifications_pb2.Header(title="Test"),
                body_text_line1="Message de test"
            )
        )

        response = await client.stub.Publish(
            notifications_pb2.PublishRequest(
                target_client_id="test-agent",
                notification=notification
            )
        )

        assert response.success
        assert response.notification_id == "test-001"

    finally:
        await client.close()
        await server.stop()

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test du rate limiting par agent"""
    # Implementation des tests de limitation de débit
    pass
```

Ces patterns constituent la base technique solide pour implémenter toasty selon les recommandations expertes. Chaque pattern est conçu pour la production avec gestion d'erreurs, observabilité et performance optimisée.