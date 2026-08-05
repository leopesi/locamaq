"""
Service class for Evolution API (WhatsApp).
Follows Single Responsibility Principle — only handles WhatsApp communication.
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger('locamaq.integrations')


class EvolutionAPIService:
    """Handles communication with Evolution API for WhatsApp messaging."""

    def __init__(self, base_url=None, api_key=None, instance=None):
        self.base_url = (base_url or settings.EVOLUTION_API_URL).rstrip('/')
        self.api_key = api_key or settings.EVOLUTION_API_KEY
        self.instance = instance or settings.EVOLUTION_INSTANCE
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json',
        }

    @classmethod
    def from_tenant(cls, tenant):
        """Create service from tenant settings."""
        return cls(
            base_url=tenant.evolution_api_url or settings.EVOLUTION_API_URL,
            api_key=tenant.evolution_api_key or settings.EVOLUTION_API_KEY,
            instance=tenant.evolution_instance or settings.EVOLUTION_INSTANCE,
        )

    def _url(self, endpoint: str) -> str:
        return f'{self.base_url}/{endpoint}/{self.instance}'

    def send_text(self, phone: str, message: str) -> dict:
        """Send a text message via WhatsApp."""
        payload = {
            'number': phone,
            'text': message,
        }
        try:
            response = requests.post(
                self._url('message/sendText'),
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            logger.info(f'WhatsApp text sent to {phone} via {self.instance}')
            return response.json()
        except requests.exceptions.ConnectionError as e:
            logger.error(f'WhatsApp connection failed: {self.base_url} — {e}')
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f'WhatsApp timeout sending to {phone} — {e}')
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f'WhatsApp HTTP error sending to {phone} — {e.response.status_code}: {e.response.text}')
            raise

    def send_media(self, phone: str, media_url: str, caption: str = '', media_type: str = 'document') -> dict:
        """Send a media file (PDF, image) via WhatsApp."""
        payload = {
            'number': phone,
            'mediatype': media_type,
            'media': media_url,
            'caption': caption,
        }
        try:
            response = requests.post(
                self._url('message/sendMedia'),
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            logger.info(f'WhatsApp media sent to {phone} via {self.instance}')
            return response.json()
        except Exception as e:
            logger.error(f'WhatsApp media error to {phone} — {e}')
            raise

    def check_connection(self) -> dict:
        """Check if the WhatsApp instance is connected."""
        response = requests.get(
            self._url('instance/connectionState'),
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
