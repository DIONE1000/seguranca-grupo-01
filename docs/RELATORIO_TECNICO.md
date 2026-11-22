# Relatório técnico simplificado — Etapa 1

## 7.1 Identificação

| Campo | Informação |
|---|---|
| Integrantes | Raimundo Dione; José Marques; terceira integrante pendente (máximo de 3) |
| Turma | 8º período — Engenharia de Software |
| Linguagem | Python 3.14.7 |
| Repositório | [github.com/DIONE1000/seguranca-grupo-01](https://github.com/DIONE1000/seguranca-grupo-01) |

## 7.2 Descrição da Solução

| Origem | Módulos usados | Papel na solução |
|---|---|---|
| Biblioteca padrão do Python | `argparse`, `pathlib`, `hashlib`, `hmac`, `os`, `sys`, `__future__.annotations` | Interface de linha de comando, caminhos e leitura de arquivos, SHA-256 e comparação de hashes, permissões de arquivo, mensagens/códigos de saída e anotações de tipos. |
| Dependência externa | `cryptography`: Ed25519, `serialization` e `InvalidSignature` | Geração e uso das chaves, assinatura/verificação Ed25519, codificação PEM e tratamento de assinaturas inválidas. |

O fluxo combina essas ferramentas: `argparse` encaminha cada comando, enquanto `pathlib` lê os arquivos como bytes. Para integridade, `hashlib` calcula o SHA-256 e `hmac.compare_digest` compara o resultado com a referência. `os` restringe as permissões da chave privada em sistemas POSIX, `sys` controla mensagens de erro e códigos de saída, e `__future__.annotations` adia a avaliação das anotações de tipo. Esses módulos já vêm com Python; por isso não aparecem em `requirements.txt`.

Para as operações criptográficas, foi escolhida a dependência externa `cryptography`, que fornece uma implementação mantida de Ed25519 e evita implementar os algoritmos no projeto. `Ed25519PrivateKey` gera a chave privada e assina os bytes originais; `Ed25519PublicKey` verifica a assinatura; `serialization` carrega e grava a chave privada em PEM PKCS#8 e a pública em PEM SubjectPublicKeyInfo; `InvalidSignature` permite rejeitar verificações inválidas. A assinatura resultante é gravada em formato binário com 64 bytes.

O código da ferramenta está em `src/seguranca.py`, os testes automatizados em `tests/`, o arquivo de exemplo em `exemplos/` e as dependências em `requirements.txt`. As respostas válidas retornam código 0; divergências retornam 1; erros de uso, arquivo ou chave retornam 2, com mensagens em português.

## 7.3 Funcionalidades Implementadas (R01 a R06)

R01 — `keygen` gera o par Ed25519; R02 — `hash` calcula SHA-256; R03 — `check` compara o hash calculado com a referência; R04 — `sign` assina o arquivo com a chave privada; R05 — `verify` valida a assinatura com a chave pública correspondente; R06 — `verify` rejeita assinatura malformada, arquivo adulterado ou chave incompatível.

## 7.4 Testes Realizados

Os sete testes passaram com Python 3.14.7 (`python -m unittest discover -s tests -v`). A tabela cobre TI01–TI06; TI04 e TI05 são verificados pelo mesmo teste de assinatura. Também foram testados arquivo ausente e prevenção de sobrescrita de chaves. A saída integral está em `docs/evidencias/testes-unitarios.txt`; os testes usam apenas arquivos binários fictícios temporários.

| ID do teste | Cenário | Resultado observado | Evidência |
|---|---|---|---|
| TI01 | Hash SHA-256 do arquivo | Passou; igual ao SHA-256 independente do conteúdo | `test_hash_sha256` |
| TI02 | Alterar arquivo e comparar hash anterior | Passou; divergência e código não zero | `test_check_matches_and_detects_changed_file` |
| TI03 | Gerar chaves Ed25519 | Passou; PEM PKCS#8 e SPKI reconhecíveis | `test_keygen_writes_pem_files` |
| TI04 | Assinar e verificar arquivo original | Passou; assinatura válida de 64 bytes | `test_sign_and_verify_and_detect_tampering` |
| TI05 | Alterar arquivo após assinatura | Passou; assinatura rejeitada | `test_sign_and_verify_and_detect_tampering` |
| TI06 | Verificar com outra chave pública | Passou; assinatura rejeitada | `test_wrong_public_key_is_rejected` |

Também passou a regressão `test_keygen_does_not_overwrite_existing_files`, que confirma que `keygen` preserva arquivos existentes, e `test_missing_file_has_clear_error`, que confirma mensagem clara e código de erro para arquivo ausente.

## 7.5 Análise Técnica e Conclusão

1. **Hash isolado:** qualquer pessoa pode calcular SHA-256; sem uma referência autenticada, o hash não identifica quem criou o documento.
2. **Chaves:** a chave privada do signatário cria a assinatura; a chave pública correspondente permite verificá-la.
3. **Alteração:** a assinatura valida os bytes originais; mudar qualquer byte altera o conteúdo verificado e faz a validação falhar.
4. **Produção:** seriam necessários armazenamento e controle de acesso às chaves, identidade verificável do signatário, rotação e revogação, auditoria, carimbo de tempo e cópias de segurança. A ferramenta, sozinha, não confirma a identidade do titular nem protege uma chave privada comprometida.
