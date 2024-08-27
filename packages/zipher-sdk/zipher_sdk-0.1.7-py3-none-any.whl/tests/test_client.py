import unittest
from unittest.mock import patch, MagicMock
from zipher.client import Client
from zipher.exceptions import MissingAPIKeyError
from zipher.models import ConfFetcherRequest


class TestClient(unittest.TestCase):

    def setUp(self):
        self.customer_id = "test_id"
        self.api_key = "test_api_key"
        self.client = Client(customer_id=self.customer_id, zipher_api_key=self.api_key)

    def test_initialization(self):
        self.assertEqual(self.client.customer_id, self.customer_id)
        self.assertEqual(self.client.zipher_api_key, self.api_key)
        # Test initialization with API key as env var
        with patch('os.getenv', return_value='env_api_key'):
            client = Client(customer_id=self.customer_id)
            self.assertEqual(client.zipher_api_key, 'env_api_key')

    def test_missing_api_key(self):
        with self.assertRaises(MissingAPIKeyError):
            client = Client(customer_id=self.customer_id)

    @patch('requests.get')
    def test_get_optimized_config_success(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.json = MagicMock(return_value={"key": "value"})

        response = self.client.get_optimized_config(job_id="1234")
        self.assertEqual(response, {"key": "value"})

    @patch('requests.get')
    def test_get_optimized_config_failure(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.raise_for_status = MagicMock(side_effect=ConnectionError("API Failure"))
        with self.assertRaises(ConnectionError):
            self.client.get_optimized_config(job_id="1234")


if __name__ == '__main__':
    unittest.main()
