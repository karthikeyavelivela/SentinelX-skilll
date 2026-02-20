import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("vulnguard.audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        # Extract user info from state if available
        user_info = "anonymous"
        
        response = await call_next(request)
        
        duration = round(time.time() - start, 4)
        logger.info(
            f"[AUDIT] {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration}s "
            f"client={request.client.host if request.client else 'unknown'}"
        )
        
        response.headers["X-Process-Time"] = str(duration)
        return response
