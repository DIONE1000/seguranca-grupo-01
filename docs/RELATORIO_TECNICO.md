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

Para desenvolver a ferramenta, combinamos módulos da biblioteca padrão do Python com uma dependência externa. Os módulos padrão já acompanham o interpretador; instalamos `cryptography`, a única biblioteca externa, por meio de `requirements.txt`.

| Origem | Bibliotecas | Como as usamos |
|---|---|---|
| Biblioteca padrão do Python | `argparse`, `pathlib`, `os`, `sys` | Interpretamos comandos, localizamos e lemos arquivos como bytes, controlamos permissões e tratamos erros e códigos de saída. |
| Biblioteca padrão do Python | `hashlib`, `hmac` | Calculamos SHA-256 e comparamos o resultado com a referência (R02 e R03). |
| Biblioteca padrão do Python | `__future__` | Adiamos a avaliação das anotações de tipo, o que facilita a leitura e a manutenção das funções tipadas. |
| Dependência externa | `cryptography` | Geramos chaves Ed25519, assinamos e verificamos arquivos e serializamos as chaves PEM (R01 e R04–R06). |

Na interface, usamos `argparse` para reconhecer os cinco comandos e receber seus argumentos. Por exemplo, em `check arquivo HASH_REFERENCIA`, ele identifica o caminho do arquivo e o hash informado. A partir desses argumentos, `pathlib` representa o caminho e permite ler o arquivo como bytes. Para os comandos `hash` e `check`, `hashlib` calcula o SHA-256 e `hmac.compare_digest` compara o resultado com o hash de referência. Essa combinação atende aos requisitos R02 e R03: calcular o resumo do arquivo e detectar divergências.

Para os requisitos de assinatura, escolhemos a dependência externa `cryptography`, porque a biblioteca padrão do Python não oferece as operações Ed25519 necessárias. Com `Ed25519PrivateKey`, geramos o par de chaves e assinamos os bytes do arquivo; com `Ed25519PublicKey`, verificamos a assinatura. O módulo `serialization`, da mesma dependência, converte as chaves para os formatos PEM exigidos: PKCS#8 para a chave privada e SubjectPublicKeyInfo para a pública. Quando a verificação encontra uma assinatura inválida, `InvalidSignature` permite tratar esse resultado e rejeitá-lo. Assim, `cryptography` fornece as operações necessárias para atender a R01 e R04–R06 sem implementarmos os algoritmos criptográficos por conta própria.

### Organização do código

Concentramos o código principal em `src/seguranca.py`. Em `build_parser()` definimos os cinco comandos e a ordem dos argumentos; em `main()` encaminhamos cada comando para a operação correspondente. Organizamos as operações em `keygen()`, `file_hash()`, `check_hash()`, `sign_file()` e `verify_file()`. As funções auxiliares `_read()`, `_write()`, `_load_private()` e `_load_public()` cuidam da leitura e gravação binária e do carregamento das chaves. Mantivemos os testes em `tests/`, o arquivo de exemplo em `exemplos/` e as evidências em `docs/evidencias/`.

### Principais decisões técnicas

Para garantir que o cálculo e a verificação considerem exatamente o conteúdo recebido, decidimos ler e processar os arquivos como bytes, sem normalização. Usamos SHA-256 para calcular o hash e Ed25519 para gerar e verificar assinaturas. Também adotamos os formatos PEM PKCS#8 e SubjectPublicKeyInfo para, respectivamente, a chave privada e a pública, além do formato binário de 64 bytes para a assinatura. No comando `check`, comparamos o hash calculado com a referência por meio de `hmac.compare_digest`. No `keygen`, impedimos a gravação sobre arquivos existentes e, em sistemas POSIX, ajustamos as permissões da chave privada para restringir seu acesso. Por fim, padronizamos os códigos de saída: 0 indica sucesso, 1 indica divergência e 2 indica erro; as mensagens correspondentes são exibidas em português.

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
