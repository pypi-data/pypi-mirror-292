from datetime import date
import unittest
from unittest.mock import MagicMock
from modelmetry.guardrails.response import GuardrailCheckResponse
from modelmetry.openapi.api.default_api import DefaultApi
from modelmetry.guardrails.client import GuardrailsClient
from modelmetry.openapi.api_response import ApiResponse
from modelmetry.openapi.models.guardrail_check import GuardrailCheck


class TestGuardrailsClient(unittest.TestCase):
    def test_instanciate_without_api_key_should_fail(self):
        with self.assertRaises(ValueError):
            GuardrailsClient("")

    def test_instanciate_normal(self):
        client = GuardrailsClient("api_key")
        self.assertIsNotNone(client)
        self.assertIsInstance(client, GuardrailsClient)
        self.assertIsInstance(client.backend, DefaultApi)
        self.assertEqual(client.api_key, "api_key")
        self.assertIsNone(client.tenant_id)

    def test_check_pass_from_api(self):
        client = GuardrailsClient("api_key")
        guardrail_id = "grd_testId"
        output_text = "Test output"

        # Call the method
        mock_response = ApiResponse(
            status_code=200,
            raw_data=b"",
            data=GuardrailCheck(
                id="check_123",
                tenant_id="test_tenant_id",
                guardrail_id="test_guardrail_id",
                outcome="pass",
                duration_ms=1000,
                payload={},
                summarised_entries=[],
                metadata={},
                created_at=date.today(),
                updated_at=date.today(),
                created_by="test_user",
                updated_by="test_user",
            ),
        )

        client.backend.check_payload_with_http_info = MagicMock(
            return_value=mock_response
        )
        result = client.check(guardrail_id=guardrail_id, output_text=output_text)

        # Assertions
        self.assertIsInstance(result, GuardrailCheckResponse)
        self.assertEqual(result.check.id, "check_123")
        self.assertTrue(result.passed)
        self.assertFalse(result.failed)
        self.assertFalse(result.errored)

    def test_check_fail_from_api(self):
        client = GuardrailsClient("api_key")
        guardrail_id = "grd_testId"
        output_text = "Test output"

        # Call the method
        mock_response = ApiResponse(
            status_code=200,
            raw_data=b"",
            data=GuardrailCheck(
                id="check_123",
                tenant_id="test_tenant_id",
                guardrail_id="test_guardrail_id",
                outcome="fail",
                duration_ms=1000,
                payload={},
                summarised_entries=[],
                metadata={},
                created_at=date.today(),
                updated_at=date.today(),
                created_by="test_user",
                updated_by="test_user",
            ),
        )

        client.backend.check_payload_with_http_info = MagicMock(
            return_value=mock_response
        )
        result = client.check(guardrail_id=guardrail_id, output_text=output_text)

        # Assertions
        self.assertIsInstance(result, GuardrailCheckResponse)
        self.assertEqual(result.check.id, "check_123")
        self.assertFalse(result.passed)
        self.assertTrue(result.failed)
        self.assertFalse(result.errored)

    def test_check_error_from_api(self):
        client = GuardrailsClient("api_key")
        guardrail_id = "grd_testId"
        output_text = "Test output"

        # Call the method
        mock_response = ApiResponse(
            status_code=200,
            raw_data=b"",
            data=GuardrailCheck(
                id="check_123",
                tenant_id="test_tenant_id",
                guardrail_id="test_guardrail_id",
                outcome="error",
                duration_ms=1000,
                payload={},
                summarised_entries=[],
                metadata={},
                created_at=date.today(),
                updated_at=date.today(),
                created_by="test_user",
                updated_by="test_user",
            ),
        )

        client.backend.check_payload_with_http_info = MagicMock(
            return_value=mock_response
        )
        result = client.check(guardrail_id=guardrail_id, output_text=output_text)

        # Assertions
        self.assertIsInstance(result, GuardrailCheckResponse)
        self.assertEqual(result.check.id, "check_123")
        self.assertFalse(result.passed)
        self.assertFalse(result.failed)
        self.assertTrue(result.errored)

    def test_check_transport_error(self):
        client = GuardrailsClient("api_key")
        guardrail_id = "grd_testId"
        output_text = "Test output"

        # Call the method and raise an exception to simulate a transport/http error other than from the backend
        # e.g., connection error, timeout, etc.
        client.backend.check_payload_with_http_info = MagicMock(
            side_effect=Exception("Transport error")
        )

        with self.assertRaises(Exception):
            result = client.check(guardrail_id=guardrail_id, output_text=output_text)

            # Assertions
            self.assertIsInstance(result, GuardrailCheckResponse)
            self.assertEqual(result.check.id, "check_123")
            self.assertFalse(result.passed)
            self.assertFalse(result.failed)
            self.assertTrue(result.errored)
            self.assertIsNotNone(result.error)
            self.assertIsInstance(result.error, Exception)
