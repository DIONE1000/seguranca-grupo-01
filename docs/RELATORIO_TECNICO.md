# Relatório técnico simplificado — Etapa 1

## 7.1 Identificação

| Campo | Informação |
|---|---|
| Integrantes | Raimundo Dione; José Marques; terceira integrante pendente (máximo de 3) |
| Turma | 8º período — Engenharia de Software |
| Linguagem | Python 3.14.7 |
| Repositório | [github.com/DIONE1000/seguranca-grupo-01](https://github.com/DIONE1000/seguranca-grupo-01) |

## 7.2 Descrição da Solução

### Bibliotecas utilizadas

Para desenvolvermos a ferramenta, combinamos módulos da biblioteca padrão do Python com a dependência externa `cryptography`. Os módulos padrão já acompanham o interpretador; a dependência externa precisa constar em `requirements.txt` e ser instalada.

| Origem | Bibliotecas | Uso e relação com os requisitos |
|---|---|---|
| Biblioteca padrão do Python | `argparse`, `pathlib`, `os`, `sys` | Recebemos comandos e argumentos, lemos arquivos como bytes e tratamos permissões, erros e códigos de saída. |
| Biblioteca padrão do Python | `hashlib`, `hmac` | Calculamos SHA-256 e comparamos o resultado com a referência (R02 e R03). |
| Biblioteca padrão do Python | `__future__.annotations` | Adiamos a avaliação das anotações de tipo para facilitar a manutenção do código. |
| Dependência externa | `cryptography` | Geramos chaves Ed25519, assinamos e verificamos arquivos e serializamos chaves PEM (R01 e R04–R06). |

Usamos `argparse` para interpretar comandos — por exemplo, `check arquivo HASH_REFERENCIA` — e `pathlib` para ler os bytes originais. Para R02 e R03, `hashlib` calcula SHA-256 e `hmac.compare_digest` compara o resultado com a referência. Para R01 e R04–R06, escolhemos `cryptography`, pois a biblioteca padrão não fornece as operações Ed25519 necessárias: `Ed25519PrivateKey` gera a chave e assina; `Ed25519PublicKey` verifica; `serialization` grava e carrega PEM PKCS#8 e SubjectPublicKeyInfo; `InvalidSignature` permite rejeitar verificações inválidas. Esses componentes fazem parte do mesmo pacote. Como os outros módulos já vêm com Python, `cryptography` é a única dependência externa listada em `requirements.txt`.

### Organização do código

Organizamos o código principal em `src/seguranca.py`: `build_parser()` define comandos e argumentos, e `main()` encaminha cada comando. As funções `keygen()`, `file_hash()`, `check_hash()`, `sign_file()` e `verify_file()` implementam as operações; `_read()`, `_write()`, `_load_private()` e `_load_public()` concentram a leitura/gravação binária e o carregamento das chaves. Mantivemos testes em `tests/`, exemplo em `exemplos/` e evidências em `docs/evidencias/`.

### Principais decisões técnicas

Decidimos processar bytes sem normalização, usar SHA-256 para integridade e Ed25519 para assinaturas, e adotar PEM PKCS#8 (chave privada) e SubjectPublicKeyInfo (pública). Gravamos assinaturas binárias de 64 bytes. `check` compara hashes com `hmac.compare_digest`; `keygen` não sobrescreve arquivos e, em sistemas POSIX, restringe a permissão da chave privada. Definimos códigos de saída 0 para sucesso, 1 para divergência e 2 para erro, com mensagens em português.

## 7.3 Funcionalidades Implementadas (R01 a R06)

R01 — `keygen` gera o par Ed25519; R02 — `hash` calcula SHA-256; R03 — `check` compara o hash calculado com a referência; R04 — `sign` assina o arquivo com a chave privada; R05 — `verify` valida a assinatura com a chave pública correspondente; R06 — `verify` rejeita assinatura malformada, arquivo adulterado ou chave incompatível.

## 7.4 Testes Realizados

Os sete testes passaram com Python 3.14.7 (`python -m unittest discover -s tests -v`). A tabela registra TI01–TI06; TI04 e TI05 compartilham o teste de assinatura. Também foram testados arquivo ausente e prevenção de sobrescrita de chaves. A saída está em `docs/evidencias/testes-unitarios.txt`; os testes usam arquivos binários fictícios temporários.

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
