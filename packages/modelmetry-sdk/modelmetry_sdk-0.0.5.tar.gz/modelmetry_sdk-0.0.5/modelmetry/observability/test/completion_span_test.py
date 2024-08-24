import unittest

import unittest
from modelmetry.openapi.models.chat_input import ChatInput
from modelmetry.openapi.models.chat_input_messages_inner import ChatInputMessagesInner
from modelmetry.openapi.models.completion_family_data_input import (
    CompletionFamilyDataInput,
)
from modelmetry.openapi.models.cost import Cost
from modelmetry.openapi.models.document import Document
from modelmetry.openapi.models.money import Money
from modelmetry.openapi.models.options import Options
from modelmetry.openapi.models.output import Output
from modelmetry.openapi.models.text_input import TextInput
from modelmetry.openapi.models.usage import Usage
from modelmetry.openapi.models.usage_value import UsageValue
from modelmetry.observability.span import CompletionSpan


class TestCompletionSpan(unittest.TestCase):
    def setUp(self):
        self.trace_id = "trace_id"
        self.tenant_id = "tenant_id"
        self.parent_id = "parent_id"
        self.name = "name"
        self.message = "message"
        self.severity = "severity"
        self.family = "family"
        self.metadata = {"key": "value"}
        self.input_text = "input_text"
        self.output_text = "output_text"
        self.messages = [ChatInputMessagesInner(message="message")]
        self.documents = [
            Document(
                Identifier="identifier",
                Title="title",
                ContentType="content_type",
                Content="content",
                Metadata={"key": "value"},
            )
        ]
        self.options = Options()
        self.output = Output(Text="text")
        self.usage = Usage(input=UsageValue(Amount=10, Unit="tokens"))
        self.cost = Cost(input=Money(Amount=10.0, Currency="USD"))

    def test_completion_span_creation(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        self.assertEqual(span.name, self.name)
        self.assertEqual(span.trace_id, self.trace_id)
        self.assertEqual(span.tenant_id, self.tenant_id)
        self.assertEqual(span.parent_id, self.parent_id)
        self.assertEqual(span.message, self.message)
        self.assertEqual(span.severity, self.severity)
        self.assertEqual(span.family, self.family)
        self.assertEqual(span.metadata, self.metadata)
        self.assertEqual(span.family_data.options, self.options)
        self.assertEqual(span.family_data.documents, self.documents)
        self.assertEqual(
            span.family_data.input,
            CompletionFamilyDataInput(TextInput(Text=self.input_text)),
        )
        self.assertEqual(span.family_data.output, self.output)
        self.assertEqual(span.family_data.usage, self.usage)
        self.assertEqual(span.family_data.cost, self.cost)

    def test_completion_span_set_model(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_model("new_model")
        self.assertEqual(span.family_data.options.model, "new_model")

    def test_completion_span_set_provider(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_provider("new_provider")
        self.assertEqual(span.family_data.options.provider, "new_provider")

    def test_completion_span_set_input(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        new_input = CompletionFamilyDataInput(TextInput(Text=self.input_text))
        span.set_input(new_input)
        self.assertEqual(span.family_data.input, new_input)

    def test_completion_span_set_input_text(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_input_text("new_input_text")
        self.assertEqual(
            span.family_data.input,
            CompletionFamilyDataInput(TextInput(Text="new_input_text")),
        )

    def test_completion_span_set_input_messages(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_input_messages(self.messages)
        self.assertEqual(
            span.family_data.input,
            CompletionFamilyDataInput(ChatInput(Messages=self.messages)),
        )

    def test_completion_span_set_output(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        new_output = Output(Text="new_text")
        span.set_output(new_output)
        self.assertEqual(span.family_data.output, new_output)

    def test_completion_span_set_output_text(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_output_text("new_text")
        self.assertEqual(span.family_data.output, Output(Text="new_text"))

    def test_completion_span_set_output_messages(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_output_messages(self.messages)
        self.assertEqual(span.family_data.output, Output(Messages=self.messages))

    def test_completion_span_set_usage(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_usage("input", 20, "tokens")
        self.assertEqual(
            span.family_data.usage.input, UsageValue(Amount=20, Unit="tokens")
        )

    def test_completion_span_set_cost(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.set_cost("input", 20.0, "USD")
        self.assertEqual(
            span.family_data.cost.input, Money(Amount=20.0, Currency="USD")
        )

    def test_completion_span_add_document(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        new_document = Document(
            Identifier="new_identifier",
            Title="new_title",
            ContentType="new_content_type",
            Content="new_content",
            Metadata={"new_key": "new_value"},
        )
        span.add_document(
            identifier=new_document.identifier,
            title=new_document.title,
            content_type=new_document.content_type,
            content=new_document.content,
            metadata=new_document.metadata,
        )
        self.assertEqual(span.family_data.documents, self.documents + [new_document])

    def test_completion_span_end(self):
        span = CompletionSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            model="model",
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            input=CompletionFamilyDataInput(TextInput(Text=self.input_text)),
            documents=self.documents,
            options=self.options,
            output=self.output,
            usage=self.usage,
            cost=self.cost,
        )

        span.end()
        self.assertIsNotNone(span.ended_at)
