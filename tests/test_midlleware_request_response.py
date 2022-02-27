from unittest import TestCase

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from loguru import logger

from fastapi_loguru.middlewares import RequestResponseLoggerMiddleware


class TestRequestResoponseLoggerMiddleware(TestCase):
    filename = "tests.loguru.log"
    logger = logger

    def setUp(self) -> None:
        super().setUp()
        ftm = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        self.logger.add(self.filename, level="INFO", format=ftm)

    def tearDown(self) -> None:
        super().tearDown()
        with open(self.filename, "r+") as f:
            f.truncate(0)

    @pytest.fixture(autouse=True)
    def add_app(self):
        app = FastAPI()

        @app.get("/success", status_code=200)
        async def success():
            return {"message": "responded with success."}

        @app.get("/failure", status_code=400)
        async def failure():
            return {"message": "responded with failure."}

        @app.get("/skip", status_code=500)
        async def skip():
            return {"message": "responded with skip."}

        skip_routes = ["/skip"]
        app.add_middleware(RequestResponseLoggerMiddleware, logger=self.logger, skip_routes=skip_routes)

        self.client = TestClient(app)

    def test_req_res_loguru_success(self):
        response: Response = self.client.get(url="/success")
        self.assertEqual(response.status_code, 200)
        with open(self.filename) as f:
            line: str = f.readline().strip()
            line: list = line.split(" | ")
            self.assertEqual(line[1], "INFO    ")
            self.assertIn("GET /success 200 OK", line[2])

    def test_req_res_loguru_failure(self):
        response: Response = self.client.get(url="/failure")
        self.assertEqual(response.status_code, 400)
        with open(self.filename) as f:
            line: str = f.readline().strip()
            line: list = line.split(" | ")
            self.assertEqual(line[1], "INFO    ")
            self.assertIn("GET /failure 400 BAD_REQUEST", line[2])

    def test_req_res_loguru_skip_routes(self):
        response: Response = self.client.get(url="/skip")
        self.assertEqual(response.status_code, 500)
        with open(self.filename) as f:
            line: str = f.readline().strip()
            self.assertEqual(line, "")  # no log found, that's correct.
