from botocore.response import StreamingBody
from localstack.state import pickle


def test_pickle_streaming_body():
    import urllib3

    http = urllib3.PoolManager()
    resp = http.request("GET", "http://www.google.com", preload_content=False)
    stream = StreamingBody(resp, content_length=None)
    blob = pickle.dumps(stream)
    restored = pickle.loads(blob)
    # assert we can read the stream after restoring it
    assert restored.read()
