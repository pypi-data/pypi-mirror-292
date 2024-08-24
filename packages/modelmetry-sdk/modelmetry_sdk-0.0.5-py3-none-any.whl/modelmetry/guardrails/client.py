from typing import List

from modelmetry import openapi
from modelmetry.guardrails.response import GuardrailCheckResponse
from modelmetry.openapi.api.default_api import DefaultApi
from modelmetry.openapi.models import CheckPayloadRequestBody
from modelmetry.openapi.models.text_input import TextInput


class GuardrailsClient:
    backend: DefaultApi = None
    tenant_id: str | None = None

    def __init__(
        self,
        # backend
        api_key: str,
        tenant_id: str | None = None,
        host="https://api.modelmetry.com",
        # opts
    ):
        if not api_key:
            raise ValueError("api_key is required to instantiate GuardrailsClient")

        self.tenant_id = tenant_id or None
        self.api_key = api_key
        self.client = openapi.ApiClient(
            openapi.Configuration(host, api_key={"apikeyAuth": api_key})
        )
        self.backend = openapi.DefaultApi(self.client)

    def check(
        self,
        guardrail_id: str,
        input_text: str = None,
        input_chat: openapi.ChatInput = None,
        output_text: str = None,
        output_chat: List[openapi.ChatInputMessagesInner] = None,
    ) -> GuardrailCheckResponse:

        input: openapi.CompletionFamilyDataInput | None = None
        output: openapi.Output | None = None

        if input_text:
            input = openapi.CompletionFamilyDataInput(TextInput(Text=input_text))

        if input_chat:
            input = openapi.CompletionFamilyDataInput(input_chat)

        if output_chat:
            output = openapi.Output(Messages=output_chat)

        if output_text and len(output_text) > 0:
            output = openapi.Output(Text=output_text)

        body = CheckPayloadRequestBody(
            TenantID=self.tenant_id or None,
            GuardrailID=guardrail_id,
            Payload=openapi.Payload(Input=input, Output=output),
        )

        try:
            res = self.backend.check_payload_with_http_info(body)
            output = GuardrailCheckResponse(check=res.data)
            return output
        except openapi.ApiException as e:
            output = GuardrailCheckResponse(error=e)
            return output
