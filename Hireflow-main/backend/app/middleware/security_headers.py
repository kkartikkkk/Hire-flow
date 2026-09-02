"""Security headers middleware.

Appends standard security HTTP headers to all API responses.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to inject security headers into every response."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # 1. Prevent Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # 2. Prevent MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 3. Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 4. Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # 5. Content Security Policy (restricted for API responses)
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        
        # 6. XSS Protection (legacy fallback)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
