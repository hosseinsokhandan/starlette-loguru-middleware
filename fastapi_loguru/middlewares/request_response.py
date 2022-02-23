from loguru import logger as loguru_logger
from logging import Logger
from http import HTTPStatus
from typing import Callable, List, Optional
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import sys


class RequestResponseLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, logger: Optional[Logger] = None, skip_routes: Optional[List] = []):
        self._skip_routes = skip_routes
        self.logger = logger
        if not self.logger:
            self.logger = loguru_logger
            fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>"
            self.logger.add(sys.stdout, level="INFO", format=fmt)
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
        response = await call_next(request)
        end = time.perf_counter()
        self.logger.info(self._generate_log(request=request, response=response, response_time=end - begin))
        return response

    def _generate_log(self, *, request: Request, response: Response, response_time: float) -> str:
        status = response.status_code
        response_time *= 1000
        return f"{request.method} {request.url.path} {status} {HTTPStatus(status).name} {int(response_time)}ms"
