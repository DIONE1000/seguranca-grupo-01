"""Ferramenta CLI de integridade SHA-256 e assinatura Ed25519."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def _read(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ValueError(f"não foi possível ler '{path}': {exc.strerror or exc}") from exc


def _write(path: Path, data: bytes, *, private: bool = False) -> None:
    try:
        path.write_bytes(data)
        if private and os.name == "posix":
            path.chmod(0o600)
    except OSError as exc:
        raise ValueError(f"não foi possível gravar '{path}': {exc.strerror or exc}") from exc


def _load_private(path: Path) -> Ed25519PrivateKey:
    try:
        key = serialization.load_pem_private_key(_read(path), password=None)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"chave privada inválida ou incompatível: '{path}'") from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError(f"a chave '{path}' não é Ed25519")
    return key


def _load_public(path: Path) -> Ed25519PublicKey:
    try:
        key = serialization.load_pem_public_key(_read(path))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"chave pública inválida ou incompatível: '{path}'") from exc
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError(f"a chave '{path}' não é Ed25519")
    return key


def keygen(private_path: Path, public_path: Path) -> None:
    if private_path.resolve() == public_path.resolve():
        raise ValueError("os caminhos da chave privada e pública devem ser diferentes")
    existing = [str(path) for path in (private_path, public_path) if path.exists()]
    if existing:
        raise ValueError(
            "não vou sobrescrever arquivo(s) existente(s): " + ", ".join(existing)
        )
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    _write(private_path, private_pem, private=True)
    try:
        _write(public_path, public_pem)
    except ValueError:
        try:
            private_path.unlink()
        except OSError:
            pass
        raise
    print(f"Par de chaves Ed25519 salvo em '{private_path}' e '{public_path}'.")


def file_hash(path: Path) -> str:
    return hashlib.sha256(_read(path)).hexdigest()


def check_hash(path: Path, reference: str) -> bool:
    if len(reference) != 64 or any(c not in "0123456789abcdefABCDEF" for c in reference):
        raise ValueError("hash de referência inválido: informe 64 caracteres hexadecimais")
    actual = file_hash(path)
    matches = hmac.compare_digest(actual, reference.lower())
    print("Hash correspondente." if matches else "Hash divergente.")
    return matches


def sign_file(file_path: Path, private_path: Path, signature_path: Path) -> None:
    signature = _load_private(private_path).sign(_read(file_path))
    if len(signature) != 64:
        raise ValueError("a biblioteca retornou uma assinatura com tamanho inesperado")
    _write(signature_path, signature)
    print(f"Assinatura Ed25519 salva em '{signature_path}'.")


def verify_file(file_path: Path, public_path: Path, signature_path: Path) -> bool:
    public_key = _load_public(public_path)
    signature = _read(signature_path)
    if len(signature) != 64:
        print("Assinatura inválida: o arquivo deve conter exatamente 64 bytes.")
        return False
    try:
        public_key.verify(signature, _read(file_path))
    except InvalidSignature:
        print("Assinatura inválida.")
        return False
    print("Assinatura válida.")
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seguranca",
        description="Hash SHA-256 e assinatura digital Ed25519 de arquivos.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    cmd = commands.add_parser("keygen", help="gera um par de chaves Ed25519")
    cmd.add_argument("chave_privada", type=Path)
    cmd.add_argument("chave_publica", type=Path)

    cmd = commands.add_parser("hash", help="calcula o SHA-256 de um arquivo")
    cmd.add_argument("arquivo", type=Path)

    cmd = commands.add_parser("check", help="compara o SHA-256 com uma referência")
    cmd.add_argument("arquivo", type=Path)
    cmd.add_argument("hash_referencia")

    cmd = commands.add_parser("sign", help="assina um arquivo com uma chave privada")
    cmd.add_argument("arquivo", type=Path)
    cmd.add_argument("chave_privada", type=Path)
    cmd.add_argument("assinatura", type=Path)

    cmd = commands.add_parser("verify", help="verifica uma assinatura Ed25519")
    cmd.add_argument("arquivo", type=Path)
    cmd.add_argument("chave_publica", type=Path)
    cmd.add_argument("assinatura", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "keygen":
            keygen(args.chave_privada, args.chave_publica)
            return 0
        if args.command == "hash":
            print(file_hash(args.arquivo))
            return 0
        if args.command == "check":
            return 0 if check_hash(args.arquivo, args.hash_referencia) else 1
        if args.command == "sign":
            sign_file(args.arquivo, args.chave_privada, args.assinatura)
            return 0
        if args.command == "verify":
            return 0 if verify_file(args.arquivo, args.chave_publica, args.assinatura) else 1
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
