import pytest
from localstack.pro.core.services.rds import engine_postgres
from localstack.pro.core.services.rds.provider import is_valid_cluster_id
from localstack.pro.core.utils.postgresql import PATCHES, patch_postgres_proxy
from postgresql_proxy.interceptors import CommandInterceptor


class TestRDS:
    def test_rewrite_queries(self):
        query = """
            CREATE TABLE teste0ab3b22 (id integer, value text);
            COPY teste0ab3b22 from 's3://rds-e3bb6c12/my/test/file.csv'
        """

        rewriter = engine_postgres.QueryRewriteHandler()
        result = rewriter.rewrite_query(query, download=False)

        assert "s3://" not in result
        assert "from '/" in result

    def test_intercept_query(self):
        # intercept a test query with bytes data appended, as sent by some frameworks like .Net ngpsql
        # (this query fails if we do not apply the patch to CommandInterceptor in postgresql.py)
        query = b"SELECT 1\x00\x03\x00\x00\x04\xa0\x00"

        def _test_query():
            interceptor = CommandInterceptor(interceptor_config={}, plugins={}, context={})
            return interceptor._intercept_query(query, [])

        # unapply patches first
        for patch in PATCHES:
            patch.undo()

        try:
            with pytest.raises(UnicodeDecodeError):
                # should raise an exception, if patch not (yet) applied
                _test_query()
            patch_postgres_proxy()
        finally:
            # re-apply patches
            for patch in PATCHES:
                patch.apply()

        # should not raise, and return the query unmodified
        assert _test_query() == query

    def test_valid_cluster_id(self):
        assert is_valid_cluster_id("test-123")
        assert is_valid_cluster_id("test123")
        assert is_valid_cluster_id("t")

        assert not is_valid_cluster_id("test-")
        assert not is_valid_cluster_id("12-test")
        assert not is_valid_cluster_id("test-123-")
        assert not is_valid_cluster_id("test--123")
        assert not is_valid_cluster_id("test---123")
        assert not is_valid_cluster_id("test_123")
