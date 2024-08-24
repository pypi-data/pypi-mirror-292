import unittest

import unittest
from datetime import datetime, timezone
from modelmetry.observability.span import RetrievalSpan, Document, RetrievalQuery


class TestRetrievalSpan(unittest.TestCase):
    def setUp(self):
        self.trace_id = "trace_id"
        self.tenant_id = "tenant_id"
        self.parent_id = "parent_id"
        self.name = "name"
        self.message = "message"
        self.severity = "severity"
        self.family = "family"
        self.metadata = {"key": "value"}
        self.queries = [
            RetrievalQuery(TextRepresentation="query1"),
            RetrievalQuery(TextRepresentation="query2"),
        ]
        self.documents = [
            Document(
                Identifier="doc1",
                Title="Document 1",
                ContentType="text/plain",
                Content="This is document 1",
            ),
            Document(
                Identifier="doc2",
                Title="Document 2",
                ContentType="text/plain",
                Content="This is document 2",
            ),
        ]
        self.retrieval_span = RetrievalSpan(
            name=self.name,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            parent_id=self.parent_id,
            message=self.message,
            severity=self.severity,
            family=self.family,
            metadata=self.metadata,
            queries=self.queries,
            documents=self.documents,
        )

    def test_retrieval_span_initialization(self):
        self.assertEqual(self.retrieval_span.name, self.name)
        self.assertEqual(self.retrieval_span.trace_id, self.trace_id)
        self.assertEqual(self.retrieval_span.tenant_id, self.tenant_id)
        self.assertEqual(self.retrieval_span.parent_id, self.parent_id)
        self.assertEqual(self.retrieval_span.message, self.message)
        self.assertEqual(self.retrieval_span.severity, self.severity)
        self.assertEqual(self.retrieval_span.family, self.family)
        self.assertEqual(self.retrieval_span.metadata, self.metadata)
        self.assertEqual(self.retrieval_span.family_data.queries, self.queries)
        self.assertEqual(self.retrieval_span.family_data.documents, self.documents)

    def test_retrieval_span_end(self):
        self.assertIsNone(self.retrieval_span.ended_at)
        self.retrieval_span.end()
        self.assertIsNotNone(self.retrieval_span.ended_at)
        self.assertIsInstance(self.retrieval_span.ended_at, datetime)
        self.assertEqual(self.retrieval_span.ended_at.tzinfo, timezone.utc)

    def test_retrieval_span_add_document(self):
        new_document = Document(
            Identifier="doc3",
            Title="Document 3",
            ContentType="text/plain",
            Content="This is document 3",
            Metadata={"key": "value"},
        )
        self.retrieval_span.add_document(
            identifier=new_document.identifier,
            title=new_document.title,
            content_type=new_document.content_type,
            content=new_document.content_type,
            metadata=new_document.metadata,
        )

        # Check if the document is added to the family_data, by comparing the Identifier
        found = False
        for document in self.retrieval_span.family_data.documents:
            if document.identifier == new_document.identifier:
                found = True
                break

        self.assertTrue(found)

    def test_retrieval_span_add_query(self):
        new_query = RetrievalQuery(TextRepresentation="query3")
        self.retrieval_span.add_query(
            text_representation=new_query.text_representation,
            embeddings=new_query.embeddings,
        )
        self.assertIn(new_query, self.retrieval_span.family_data.queries)
