# Relatório técnico simplificado — Etapa 1

## Identificação

| Campo | Informação |
|---|---|
| Integrantes | Raimundo Dione; José Marques; terceira integrante pendente (máximo de 3) |
| Turma | 8º período — Engenharia de Software |
| Linguagem | Python 3.10+ |
| Repositório | [github.com/DIONE1000/seguranca-grupo-01](https://github.com/DIONE1000/seguranca-grupo-01) |

## Solução e funcionalidades

A CLI `src/seguranca.py` usa `cryptography` para Ed25519 e a biblioteca padrão `hashlib` para SHA-256. `keygen` grava chave privada PEM PKCS#8 sem senha e chave pública PEM SubjectPublicKeyInfo. `hash` lê bytes e imprime 64 caracteres hexadecimais minúsculos. `check` compara com referência hexadecimal. `sign` assina diretamente os bytes do arquivo e grava os 64 bytes binários da assinatura. `verify` valida esses bytes e rejeita assinaturas malformadas, adulteração e chave pública não correspondente. Os comandos de verificação retornam 0 somente quando a comparação/assinatura é válida; divergência retorna 1 e erro de uso/arquivo/chave retorna código diferente de zero (2 para erros tratados). Mensagens de erro são apresentadas em português.

O código da ferramenta está em `src/seguranca.py`, os testes automatizados em `tests/`, o arquivo de exemplo em `exemplos/` e as dependências em `requirements.txt`.

## Testes realizados

Executados com `python -m unittest discover -s tests -v`; os sete métodos de teste passaram. Eles cobrem os seis cenários TI01–TI06: TI04 (validar assinatura original) e TI05 (rejeitar arquivo adulterado) são verificados pelo mesmo método. Dois métodos extras verificam arquivo ausente e preservação de arquivos ao gerar chaves. A saída integral está registrada em `docs/evidencias/testes-unitarios.txt`. Os testes em `tests/test_segurança.py` usam apenas documentos binários fictícios temporários.

| ID | Cenário | Resultado observado | Evidência |
|---|---|---|---|
| TI01 | Hash SHA-256 do arquivo | Passou; igual ao SHA-256 independente do conteúdo | `test_hash_sha256` |
| TI02 | Alterar arquivo e comparar hash anterior | Passou; divergência e código não zero | `test_check_matches_and_detects_changed_file` |
| TI03 | Gerar chaves Ed25519 | Passou; PEM PKCS#8 e SPKI reconhecíveis | `test_keygen_writes_pem_files` |
| TI04 | Assinar e verificar arquivo original | Passou; assinatura válida de 64 bytes | `test_sign_and_verify_and_detect_tampering` |
| TI05 | Alterar arquivo após assinatura | Passou; assinatura rejeitada | `test_sign_and_verify_and_detect_tampering` |
| TI06 | Verificar com outra chave pública | Passou; assinatura rejeitada | `test_wrong_public_key_is_rejected` |

Também passou a regressão `test_keygen_does_not_overwrite_existing_files`, que confirma que `keygen` preserva arquivos existentes, e `test_missing_file_has_clear_error`, que confirma mensagem clara e código de erro para arquivo ausente.

## Análise e conclusão

SHA-256 isolado não comprova autoria: qualquer pessoa pode calcular o hash de um arquivo. A chave privada cria a assinatura digital; a chave pública correspondente verifica autenticidade e integridade em relação àquela chave. Alterar qualquer byte do documento faz a verificação falhar. Para produção seriam necessários armazenamento e controle de acesso seguros às chaves, identidade verificável do signatário, rotação e revogação, auditoria, carimbo de tempo e cópias de segurança. A ferramenta não estabelece por si só a identidade do titular da chave nem protege uma chave privada comprometida.
