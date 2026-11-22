# Relatório técnico simplificado — Etapa 1

## 7.1 Identificação

| Campo | Dados |
|---|---|
| Integrantes | Raimundo Dione; José Marques; Patricia Rebeca |
| Turma | 8º período — Engenharia de Software |
| Linguagem | Python 3.14.7 |
| Repositório | [github.com/DIONE1000/seguranca-grupo-01](https://github.com/DIONE1000/seguranca-grupo-01) |

## 7.2 Descrição da Solução

A CLI em `src/seguranca.py` usa `argparse` para oferecer `keygen`, `hash`, `check`, `sign` e `verify`. Os módulos padrão `pathlib` e `hashlib` leem arquivos como bytes e calculam SHA-256; `hmac.compare_digest` compara o hash calculado com a referência. A dependência `cryptography` fornece Ed25519 e serialização PEM: chave privada PKCS#8, chave pública SubjectPublicKeyInfo e assinatura binária de 64 bytes.

A ferramenta processa os bytes originais, sem normalização. O código de saída é 0 em caso válido, 1 para divergência ou assinatura inválida e 2 para erro de uso ou leitura. `keygen` evita sobrescrever arquivos existentes. A implementação está em `src/`, os testes automatizados em `tests/` e suas evidências em `docs/evidencias/`.

## 7.3 Funcionalidades Implementadas (R01 a R06)

R01 — geração de par Ed25519; R02 — cálculo SHA-256; R03 — comparação com hash de referência; R04 — assinatura dos bytes do arquivo; R05 — verificação com a chave pública correspondente; R06 — rejeição de assinatura inválida, adulteração ou chave incompatível.

## 7.4 Testes Realizados

A suíte automatizada executou sete métodos e todos passaram. Os seis cenários mínimos estão relacionados abaixo. Os arquivos usados nos testes são fictícios e temporários. A saída completa, com data, commit, versão do Python e comando, está em `docs/evidencias/testes_automatizados.txt`.

| ID | Cenário | Resultado | Evidência automatizada |
|---|---|---|---|
| TI01 | Calcular SHA-256 | Hash correto | `test_hash_sha256` — `testes_automatizados.txt` |
| TI02 | Alterar arquivo e comparar com hash original | Divergência detectada | `test_check_matches_and_detects_changed_file` — `testes_automatizados.txt` |
| TI03 | Gerar par de chaves | PEM válido | `test_keygen_writes_pem_files` — `testes_automatizados.txt` |
| TI04 | Assinar e verificar arquivo original | Assinatura válida | `test_sign_and_verify_and_detect_tampering` — `testes_automatizados.txt` |
| TI05 | Alterar arquivo após assinatura | Assinatura rejeitada | `test_sign_and_verify_and_detect_tampering` — `testes_automatizados.txt` |
| TI06 | Verificar com outra chave pública | Assinatura rejeitada | `test_wrong_public_key_is_rejected` — `testes_automatizados.txt` |

## 7.5 Análise Técnica e Conclusão

1. **Hash isolado:** qualquer pessoa pode calcular SHA-256; sem uma referência autenticada, ele não comprova autoria.
2. **Chaves:** a chave privada cria a assinatura; a chave pública correspondente permite verificá-la.
3. **Alteração:** a assinatura valida os bytes assinados; alterar o arquivo faz a verificação falhar.
4. **Produção:** seriam necessários armazenamento seguro de chaves, validação de identidade, rotação e revogação, auditoria e cópias de segurança. A ferramenta não implementa esses controles.
