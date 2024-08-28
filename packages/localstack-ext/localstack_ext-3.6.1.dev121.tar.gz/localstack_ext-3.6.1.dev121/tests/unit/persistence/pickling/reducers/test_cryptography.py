from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from localstack.state import pickle


def test_pickle_cryptography_rsa_key():
    obj = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    plaintext = b"foobar 123"
    encrypted = obj.public_key().encrypt(plaintext, PKCS1v15())

    # perform key serialization roundtrip
    blob = pickle.dumps(obj)
    restored_key = pickle.loads(blob)

    # decrypt bytes with restored key
    result = restored_key.decrypt(encrypted, PKCS1v15())
    assert result == plaintext


def test_pickle_cryptography_ecc_key():
    obj = ec.generate_private_key(ec.SECP256R1())

    plaintext = b"foobar 123"
    signature = obj.sign(plaintext, ec.ECDSA(hashes.SHA256()))

    blob = pickle.dumps(obj)
    restored_key = pickle.loads(blob)
    assert restored_key

    public_key = obj.public_key()
    public_key.verify(signature, plaintext, ec.ECDSA(hashes.SHA256()))
