import unittest
from unittest.mock import patch

from jalert.fetch import FetchError
from jalert.push import push_serverchan


class ServerChanErrorTests(unittest.TestCase):
    def test_request_error_does_not_include_sendkey_endpoint(self):
        secret = "SCT-test-secret"
        with patch("jalert.push.http_request", side_effect=FetchError(
                f"https://sctapi.ftqq.com/{secret}.send -> URLError: certificate error")):
            result = push_serverchan(secret, "title", "body")

        self.assertFalse(result["ok"])
        self.assertNotIn(secret, result["detail"])
        self.assertEqual(result["detail"], "URLError: certificate error")


if __name__ == "__main__":
    unittest.main()
