from localstack.pro.core.services.iot import query_docs


class TestQueryDocuments:
    def test_query_documents(self):
        docs = [
            {"s1": "v1", "n1": 1, "foo": "bar"},
            {"s1": "v2", "n2": 2, "foo": "bar"},
            {"s1": "v3", "n3": 3, "foo": "bar"},
        ]

        query = "foo bar"
        result = query_docs.query_documents(query, docs)
        assert result == []

        query = "foo:bar"
        result = query_docs.query_documents(query, docs)
        assert len(result) == 3

        query = "v2"
        result = query_docs.query_documents(query, docs)
        assert len(result) == 1
