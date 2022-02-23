from fastapi import Response
from fastapi.testclient import TestClient
from fastapi_loguru.middlewares.request_response import RequestResponseLoggerMiddleware
from loguru import logger
from tests.request_response.app import app
from unittest import TestCase

filename = "tests/request_response/req_res_middle.log"
fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>"
logger.add(filename, level="INFO", format=fmt)

app.add_middleware(RequestResponseLoggerMiddleware, logger=logger)

client = TestClient(app)

class TestRequestResoponseLoggerMiddleware(TestCase):

    def tearDown(self) -> None:
        super().tearDown()
        with open(filename, "r+") as f:
            f.truncate(0)

        """
            2022-02-23 15:51:41.455 | INFO     | GET /failure 400 BAD_REQUEST 0ms
            2022-02-23 15:51:41.459 | INFO     | GET /success 200 OK 0ms
        """

    def test_req_res_time_success(self):
        response: Response = client.get(url="/success")
        self.assertEqual(response.status_code, 200)
        with open(filename) as f:
            line: str = f.readline().strip()
            line: list = line.split(" | ")
            self.assertEqual(line[1], "INFO    ")
            self.assertEqual(line[2], "GET /success 200 OK 0ms")


    def test_req_res_time_failure(self):
        response: Response = client.get(url="/failure")
        self.assertEqual(response.status_code, 400)
        with open(filename) as f:
            line: str = f.readline().strip()
            line: list = line.split(" | ")
            self.assertEqual(line[1], "INFO    ")
            self.assertEqual(line[2], "GET /failure 400 BAD_REQUEST 0ms")