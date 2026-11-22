import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "src" / "seguranca.py"


class CliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp.name)
        self.file = self.dir / "documento.bin"
        self.file.write_bytes(b"documento academico ficticio\x00\xff")
        self.private = self.dir / "privada.pem"
        self.public = self.dir / "publica.pem"
        self.signature = self.dir / "assinatura.sig"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, str(CLI), *map(str, args)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )

    def test_hash_sha256(self):
        result = self.run_cli("hash", self.file)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), hashlib.sha256(self.file.read_bytes()).hexdigest())

    def test_check_matches_and_detects_changed_file(self):
        reference = hashlib.sha256(self.file.read_bytes()).hexdigest()
        self.assertEqual(self.run_cli("check", self.file, reference).returncode, 0)
        self.file.write_bytes(b"adulterado")
        result = self.run_cli("check", self.file, reference)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("divergente", result.stdout)

    def test_keygen_writes_pem_files(self):
        result = self.run_cli("keygen", self.private, self.public)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.private.read_bytes().startswith(b"-----BEGIN PRIVATE KEY-----"))
        self.assertTrue(self.public.read_bytes().startswith(b"-----BEGIN PUBLIC KEY-----"))

    def test_keygen_does_not_overwrite_existing_files(self):
        self.private.write_bytes(b"preservar")
        result = self.run_cli("keygen", self.private, self.public)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.private.read_bytes(), b"preservar")
        self.assertFalse(self.public.exists())

    def test_sign_and_verify_and_detect_tampering(self):
        self.assertEqual(self.run_cli("keygen", self.private, self.public).returncode, 0)
        self.assertEqual(self.run_cli("sign", self.file, self.private, self.signature).returncode, 0)
        self.assertEqual(self.signature.stat().st_size, 64)
        self.assertEqual(self.run_cli("verify", self.file, self.public, self.signature).returncode, 0)
        self.file.write_bytes(b"documento adulterado")
        result = self.run_cli("verify", self.file, self.public, self.signature)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inválida", result.stdout)

    def test_wrong_public_key_is_rejected(self):
        other_private = self.dir / "outra-privada.pem"
        other_public = self.dir / "outra-publica.pem"
        self.run_cli("keygen", self.private, self.public)
        self.run_cli("keygen", other_private, other_public)
        self.run_cli("sign", self.file, self.private, self.signature)
        result = self.run_cli("verify", self.file, other_public, self.signature)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inválida", result.stdout)

    def test_missing_file_has_clear_error(self):
        result = self.run_cli("hash", self.dir / "ausente.bin")
        self.assertEqual(result.returncode, 2)
        self.assertIn("não foi possível ler", result.stderr)


if __name__ == "__main__":
    unittest.main()
