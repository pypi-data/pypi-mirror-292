from localstack.state import pickle
from moto.acm.models import CertBundle


def test_pickle_acm_certificate():
    obj = CertBundle.generate_cert(
        "test@domain.com",
        account_id="000000000000",
        region="us-east-1",
    )
    # marshalling roundtrip
    blob = pickle.dumps(obj)
    restored: CertBundle = pickle.loads(blob)  # noqa

    assert obj._cert == restored._cert
