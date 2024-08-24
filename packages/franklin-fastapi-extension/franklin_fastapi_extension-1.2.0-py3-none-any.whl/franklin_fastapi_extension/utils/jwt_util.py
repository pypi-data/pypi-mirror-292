from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import jwt
from datetime import datetime, timedelta

_KEYS:dict[str, RSAPrivateKey | RSAPublicKey | None] = {
    "private": None,
    "public": None
}

def generate_keys(public_exponent=65537,key_size=2048):
    if _KEYS["private"] is None or _KEYS["public"] is None:
        private_key = rsa.generate_private_key(
            public_exponent=public_exponent,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        _KEYS["private"] = private_key
        _KEYS["public"] = public_key

def _get_private_key_pem() -> bytes:
    if _KEYS["private"] is None:
        raise ValueError("Private key not generated. Call 'generate_keys()' first.")

    pem = _KEYS["private"].private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem

def _get_public_key_pem() -> bytes:
    if _KEYS["public"] is None:
        raise ValueError("Public key not generated. Call 'generate_keys()' first.")

    pem = _KEYS["public"].public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

def encode(payload: dict, algorithm='RS256', exp: timedelta = timedelta(minutes=15)) -> str:
    if _KEYS["private"] is None:
        raise ValueError("Private key not generated. Call 'generate_keys()' first.")

    # Merge the provided payload with the default payload
    default_payload ={
        "exp": datetime.now() + exp
    }
    payload.update(default_payload)

    return jwt.encode(payload, _get_private_key_pem(), algorithm=algorithm)

def decode(token: str, verify: dict=None) -> dict:
    if _KEYS["public"] is None:
        raise ValueError("Public key not generated. Call 'generate_keys()' first.")
    return jwt.decode(
        token,
        _get_public_key_pem(),
        verify={
            "exp": True
        } if verify is None else verify
    )