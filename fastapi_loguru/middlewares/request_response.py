import time
from http import HTTPStatus
from typing import Callable, List, Optional

from fastapi import FastAPI, Request, Response
from loguru._logger import Logger
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


def get_request_response_logger():
    fmt: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    logger.add(sink=sys.stdout, level="INFO", format=fmt)
    return logger


class RequestResponseLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, logger: Optional[Logger] = None, skip_routes: List[str] = []):
        self._skip_routes: List[str] = skip_routes
        self.logger: Logger = logger if logger else get_request_response_logger()
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if self._should_skip_route(request):
            return await call_next(request)
        return await self._log_it(request=request, call_next=call_next)

    def _should_skip_route(self, request: Request) -> bool:
        for path in self._skip_routes:
            if request.url.path.startswith(path):
                return True
        return False

    async def _log_it(self, *, request: Request, call_next: Callable) -> Response:
        begin = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            self.logger.exception(f"Request failed at {request.method} {request.url.path}")
            raise
        end = time.perf_counter()
        self.logger.info(self._generate_log(request=request, response=response, response_time=end - begin))
        return response

    def _generate_log(self, *, request: Request, response: Response, response_time: float) -> str:
        status = response.status_code
        response_time *= 1000
        http_status_name = HTTPStatus(status).name  # pylint: disable=no-member
        return f"{request.method} {request.url.path} {status} {http_status_name} {int(response_time)}ms"
