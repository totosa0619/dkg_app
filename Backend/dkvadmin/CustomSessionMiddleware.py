from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

import logging

logger = logging.getLogger('django')

class DynamicSessionCookieDomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        " Set the session cookie domain based on the request domain  "
        # Extract the host from the request (without the port)
        host = request.get_host().split(':')[0]
        logger.info(f"Host from request of middleware: {host}")
        # Set SESSION_COOKIE_DOMAIN based on the request domain
        if host.endswith('.dkv.global'):
            # If the domain matches, set the default SESSION_COOKIE_DOMAIN
            settings.SESSION_COOKIE_DOMAIN = ".dkv.global"
            logger.info(f"Setting SESSION_COOKIE_DOMAIN to .dkv.global for host {host}")
        else:
            # Otherwise, clear the SESSION_COOKIE_DOMAIN
            settings.SESSION_COOKIE_DOMAIN = None
            logger.info(f"Clearing SESSION_COOKIE_DOMAIN for host {host}")

    def process_response(self, request, response):
        # Optionally, reset the SESSION_COOKIE_DOMAIN after the response is processed
        settings.SESSION_COOKIE_DOMAIN = ".dkv.global"
        logger.info("Resetting SESSION_COOKIE_DOMAIN to .dkv.global after response is processed")
        return response
