from typing import List

from modelmetry import openapi
from modelmetry.guardrails.client import GuardrailsClient
from modelmetry.openapi.models import CheckPayloadRequestBody, GuardrailCheck
from modelmetry.observability.client import ObservabilityClient
from modelmetry.openapi.models.text_input import TextInput


class GuardrailCheckOutput:
    """
    Represents an object with ID and Passed fields.
    """

    def __init__(self, call: GuardrailCheck):
        """
        Initializes the GuardrailCheckOutput with ID and Passed fields.

        Parameters:
            call (Call): The Call object in its entirety from the response.
        """
        self.Call = call
        self.Passed = True if call.outcome == "pass" else False
        self.Failed = True if call.outcome == "fail" else False
        self.Errored = True if call.outcome == "error" else False

    def __str__(self):
        return f"GuardrailCheckOutput(ID={self.Call.id}, Passed={self.Passed} Failed={self.Failed} Errored={self.Errored})"

    def __repr__(self):
        return f"GuardrailCheckOutput(ID={self.Call.id}, Passed={self.Passed} Failed={self.Failed} Errored={self.Errored})"


class Client:
    _configuration: openapi.Configuration = None
    _observability: ObservabilityClient = None
    _guardrails: GuardrailsClient = None

    def __init__(self, api_key: str, tenant_id: str, host="https://api.modelmetry.com"):
        self.tenant_id = tenant_id
        self.api_key = api_key
        self._configuration = openapi.Configuration(
            host,
            api_key={"apikeyAuth": api_key},
        )

    def observability(self) -> ObservabilityClient:
        if not self._observability:
            self._observability = ObservabilityClient(
                tenant_id=self.tenant_id,
                api_key=self.api_key,
                host=self._configuration.host,
            )
        return self._observability

    def guardrails(self) -> GuardrailsClient:
        if not self._guardrails:
            self._guardrails = GuardrailsClient(
                api_key=self.api_key,
                tenant_id=self.tenant_id,
                host=self._configuration.host,
            )
        return self._guardrails

    def shutdown(self):
        self.observability().shutdown()
