import pytest
from localstack.pro.core.services.kinesisanalytics.query_utils import (
    rewrite_query_for_siddhi,
    run_beam_query,
    run_flink_query,
)

TEST_QUERY = """
    CREATE OR REPLACE STREAM mystream (
        symbol VARCHAR(20), price float, message LONG)
    DESCRIPTION 'Head of webwatcher stream processing';
    SELECT STREAM * FROM mystream WHERE volume < 150;
"""


class TestKinesisAnalytics:
    def test_rewrite_queries(self):
        query = rewrite_query_for_siddhi(TEST_QUERY)
        assert "DEFINE STREAM mystream" in query
        assert "@info(name='OutStream') FROM" in query
        assert "FROM mystream[volume < 150]" in query
        assert "INSERT INTO OutStream;" in query

    # TODO remove
    @pytest.mark.skip
    def test_flink_query(self):
        def _input():
            for i in range(10):
                yield {"symbol": "s1", "price": i, "volume": 100}

        input_streams = {"mystream": _input}
        run_flink_query(TEST_QUERY, input_streams)

    # TODO remove
    @pytest.mark.skip
    def test_beam_query(self):
        def _input():
            for i in range(10):
                yield {"symbol": "s1", "price": i, "volume": 100}

        input_streams = {"mystream": _input}
        query = "SELECT * FROM PCollection"
        run_beam_query(query, input_streams)
