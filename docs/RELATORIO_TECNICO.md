# Relatório técnico simplificado — Etapa 1

## 7.1 Identificação

| Campo | Dados |
|---|---|
| Integrantes | Raimundo Dione; José Marques; Patricia Rebeca |
| Turma | 8º período — Engenharia de Software |
| Linguagem | Python 3.14.7 |
| Repositório | [github.com/DIONE1000/seguranca-grupo-01](https://github.com/DIONE1000/seguranca-grupo-01) |

## 7.2 Descrição da Solução

A CLI está em `src/seguranca.py`. `argparse` organiza os comandos e argumentos. `pathlib` representa os caminhos; `hashlib` calcula SHA-256 e `hmac.compare_digest` compara o resultado com a referência. A biblioteca `cryptography` implementa Ed25519 e a serialização PEM nos formatos PKCS#8 (privada) e SubjectPublicKeyInfo (pública).

As operações ficam nas funções `keygen`, `file_hash`, `check_hash`, `sign_file` e `verify_file`; auxiliares leem, gravam e carregam chaves. Os testes estão em `tests/test_seguranca.py`, o documento fictício em `exemplos/documento.txt` e as evidências em `docs/evidencias/`.

Os arquivos são lidos como bytes, sem conversão ou normalização. SHA-256 é exibido como 64 dígitos hexadecimais minúsculos. Ed25519 assina os bytes originais, sem pré-hash feito pela aplicação, e produz assinatura binária de 64 bytes. `keygen` evita sobrescrever arquivos. Em POSIX, a chave privada recebe permissão 600; o PEM não é cifrado por senha. Os códigos são 0 para sucesso, 1 para hash divergente ou assinatura inválida e 2 para erro de uso ou leitura, com mensagens em português.

## 7.3 Funcionalidades Implementadas (R01 a R06)

R01 — gera par Ed25519; R02 — calcula SHA-256; R03 — compara o hash com a referência; R04 — assina o arquivo com a chave privada; R05 — verifica com a chave pública correspondente; R06 — rejeita assinatura inválida, adulteração e chave incompatível. A ferramenta não estabelece por si só a identidade do titular da chave pública.

## 7.4 Testes Realizados

A suíte executou sete métodos automatizados, todos aprovados. Os seis cenários mínimos estão abaixo; TI04 e TI05 são verificados pelo mesmo método, que testa o arquivo original e depois o arquivo adulterado. Dois métodos adicionais verificam proteção contra sobrescrita e erro de arquivo ausente. Os testes usam conteúdo fictício e arquivos temporários. A saída integral, incluindo data, commit, Python e comando, está em `docs/evidencias/testes_automatizados.txt`.

| ID | Cenário e resultado | Método no log de evidências |
|---|---|---|
| TI01 | SHA-256 calculado corretamente | [`test_hash_sha256`](evidencias/testes_automatizados.txt) |
| TI02 | Alteração detectada ao comparar com hash original | [`test_check_matches_and_detects_changed_file`](evidencias/testes_automatizados.txt) |
| TI03 | Chaves PEM Ed25519 válidas e correspondentes | [`test_keygen_writes_pem_files`](evidencias/testes_automatizados.txt) |
| TI04 | Assinatura do original verificada como válida | [`test_sign_and_verify_and_detect_tampering`](evidencias/testes_automatizados.txt) |
| TI05 | Assinatura rejeitada após adulteração | [`test_sign_and_verify_and_detect_tampering`](evidencias/testes_automatizados.txt) |
| TI06 | Assinatura rejeitada com outra chave pública | [`test_wrong_public_key_is_rejected`](evidencias/testes_automatizados.txt) |

## 7.5 Análise Técnica e Conclusão

1. **Autoria e hash:** SHA-256 é público e qualquer pessoa pode recalculá-lo. Sem uma referência autenticada, alguém pode alterar o documento e substituir também o hash; ele detecta diferenças, mas não prova quem criou o arquivo.
2. **Chaves:** o titular usa a chave privada para assinar. A chave pública correspondente permite verificar a assinatura e detectar se o conteúdo mudou; sua associação à identidade do titular precisa ser confiável.
3. **Alteração:** a assinatura cobre os bytes exatos do documento. Após qualquer mudança, a verificação desses novos bytes falha.
4. **Uso em produção:** seria necessário cifrar e controlar o acesso à chave privada, validar a identidade e a distribuição das chaves públicas, planejar rotação e revogação, manter auditoria, cópias de segurança e recuperação. A CLI não oferece gestão de identidade, certificados, revogação, carimbo de tempo ou auditoria.
