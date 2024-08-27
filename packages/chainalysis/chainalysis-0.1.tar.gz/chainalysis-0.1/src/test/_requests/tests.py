import unittest
from json import JSONDecodeError
from unittest import mock

import tenacity

from chainalysis.util_functions.exceptions import (
    BadRequest,
    DataSolutionsAPIException,
    InternalServerException,
)
from chainalysis.util_functions.requests import (
    get_headers,
    issue_request,
    retry_condition,
)

mocked_successful_json = {
    "status": "success",
    "stats": {"count": 1, "size": 657, "time": 1, "truncated": "false"},
    "results": [
        {
            "block_number": 142572,
            "block_hash": "000000000000057d13a731f556c24a1318bcbb4df7d537ef07c8c813c0dc1b37",
            "timestamp": "2011-08-25T22:07:41Z",
            "median_timestamp": "2011-08-25T21:28:01Z",
            "parent_blockhash": "000000000000048edbb6c004b3fce541b5004fee9729a8b1710cb488a974d959",
            "merkleroot": "fbcf9d2616f5b8beebb21eff7186a1acc31c1bf25a71e61e2d989d2394c4d2bb",
            "version": 1,
            "version_hex": "00000001",
            "size": 44437,
            "stripped_size": 44437,
            "weight": 177748,
            "bits": "1a094a86",
            "transaction_count": 99,
            "chainwork": "0000000000000000000000000000000000000000000000050db82b769ce8b7f0",
            "nonce": 897686037.0,
            "difficulty": 1805700.836193673,
            "__confirmed": "true",
        }
    ],
    "message": "error",
}


class MockedResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

    @property
    def ok(self):
        return self.status_code < 400


class MockedResponseJsonDecodeError:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        raise JSONDecodeError("", "", 1)

    @property
    def ok(self):
        return self.status_code < 400


class MockedResponseErrorWithJsonDecoded:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

    @property
    def ok(self):
        return self.status_code < 400


class RequestsTests(unittest.TestCase):
    @mock.patch("chainalysis.util_functions.requests.request")
    def test_successful_query(self, mock_request: mock.Mock):
        mock_request.return_value = MockedResponse(
            200,
            mocked_successful_json,
        )
        response = issue_request(
            url="success",
            api_key="dummy_api_key",
            method="GET",
        )

        self.assertEqual(response["status"], "success")
        self.assertEqual(response["status"], "success")

    @mock.patch("chainalysis.util_functions.requests.request")
    @mock.patch("tenacity.nap.time.sleep", mock.MagicMock())
    def test_json_decode_error(self, mock_request: mock.Mock):
        mock_request.return_value = MockedResponseJsonDecodeError(
            200,
            mocked_successful_json,
        )

        with self.assertRaises(tenacity.RetryError) as retry_context:
            issue_request(
                url="failure",
                api_key="dummy_api_key",
                method="GET",
            )
        self.assertIsInstance(
            retry_context.exception.last_attempt.exception(), DataSolutionsAPIException
        )

    @mock.patch("chainalysis.util_functions.requests.request")
    @mock.patch("tenacity.nap.time.sleep", mock.MagicMock())
    def test_json_decode_error_inside(self, mock_request: mock.Mock):
        mock_request.return_value = MockedResponseJsonDecodeError(
            400,
            mocked_successful_json,
        )

        with self.assertRaises(tenacity.RetryError) as retry_context:
            issue_request(
                url="failure",
                api_key="dummy_api_key",
                method="GET",
            )
        self.assertIsInstance(
            retry_context.exception.last_attempt.exception(), DataSolutionsAPIException
        )

    @mock.patch("chainalysis.util_functions.requests.request")
    @mock.patch("tenacity.nap.time.sleep", mock.MagicMock())
    def test_error_with_no_decode_issue(self, mock_request: mock.Mock):
        mock_request.return_value = MockedResponseErrorWithJsonDecoded(
            300,
            mocked_successful_json,
        )

        with self.assertRaises(tenacity.RetryError) as retry_context:
            issue_request(
                url="failure",
                api_key="dummy_api_key",
                method="GET",
            )
        self.assertIsInstance(
            retry_context.exception.last_attempt.exception(), DataSolutionsAPIException
        )

    @mock.patch("chainalysis.util_functions.requests.request")
    @mock.patch("tenacity.nap.time.sleep", mock.MagicMock())
    def test_error_bad_request_error(self, mock_request: mock.Mock):
        mock_request.return_value = MockedResponseErrorWithJsonDecoded(
            400,
            mocked_successful_json,
        )

        with self.assertRaises(BadRequest) as retry_context:
            issue_request(
                url="failure",
                api_key="dummy_api_key",
                method="GET",
            )

    @mock.patch("chainalysis.util_functions.requests.request")
    @mock.patch("tenacity.nap.time.sleep", mock.MagicMock())
    def test_api_exception_inside(self, mock_request: mock.Mock):
        mock_request.return_value = MockedResponseJsonDecodeError(
            400,
            mocked_successful_json,
        )

        with self.assertRaises(tenacity.RetryError) as retry_context:
            issue_request(
                url="failure",
                api_key="dummy_api_key",
                method="GET",
            )
        self.assertIsInstance(
            retry_context.exception.last_attempt.exception(), DataSolutionsAPIException
        )

    @mock.patch("chainalysis.util_functions.requests.request")
    @mock.patch("tenacity.nap.time.sleep", mock.MagicMock())
    def test_internal_exception(self, mock_request: mock.Mock):
        mock_request.side_effect = InternalServerException()

        with self.assertRaises(tenacity.RetryError) as retry_context:
            issue_request(
                url="failure",
                api_key="dummy_api_key",
                method="GET",
            )
        self.assertIsInstance(
            retry_context.exception.last_attempt.exception(), InternalServerException
        )

    def test_get_headers(self):
        api_key = "API KEY"
        expected_headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        result = get_headers(api_key)

        self.assertEqual(result, expected_headers)

    def test_retry_exception(self):
        self.assertEqual(retry_condition(BadRequest()), False)


if __name__ == "__main__":
    unittest.main()
