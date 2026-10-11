from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


class Ed25519Signer:
    @staticmethod
    def generate_keypair() -> tuple[bytes, bytes]:
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return private_bytes, public_bytes

    @staticmethod
    def sign_bytes(private_key_bytes: bytes, data: bytes) -> bytes:
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        return private_key.sign(data)

    @staticmethod
    def verify_bytes(public_key_bytes: bytes, data: bytes, signature: bytes) -> bool:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        try:
            public_key.verify(signature, data)
            return True
        except InvalidSignature:
            return False
