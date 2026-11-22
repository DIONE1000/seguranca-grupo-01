# Ferramenta de integridade e assinatura digital

CLI em Python para calcular e comparar hashes SHA-256 e gerar/verificar assinaturas Ed25519 em arquivos. Os arquivos são sempre lidos como bytes, sem conversão ou normalização.

## Requisitos

- Python 3.10 ou superior
- Dependência `cryptography` listada em `requirements.txt`

## Instalação

```shell
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução

No Windows, substitua `python` por `py` se necessário. A ordem dos argumentos segue o contrato da atividade.

```shell
python src/seguranca.py keygen chave_privada.pem chave_publica.pem
python src/seguranca.py hash documento.txt
python src/seguranca.py check documento.txt HASH_REFERENCIA
python src/seguranca.py sign documento.txt chave_privada.pem assinatura.sig
python src/seguranca.py verify documento.txt chave_publica.pem assinatura.sig
```

`hash` imprime o SHA-256 com 64 caracteres hexadecimais minúsculos. `check` informa se o valor corresponde. `sign` grava exatamente 64 bytes de assinatura Ed25519; `verify` informa se ela é válida. Para `check` e `verify`, o código de saída é `0` em caso válido e diferente de zero em caso de divergência ou erro. Erros de uso ou de arquivo retornam `2` com mensagem em português.

As chaves são gravadas em PEM: privada PKCS#8 sem senha e pública SubjectPublicKeyInfo. Proteja a chave privada e não a publique em repositórios.

## Exemplos

```shell
python src/seguranca.py keygen privada.pem publica.pem
python src/seguranca.py hash exemplos/documento.txt
# Passe o hash obtido como referência:
python src/seguranca.py check exemplos/documento.txt HASH_SHA256
python src/seguranca.py sign exemplos/documento.txt privada.pem documento.sig
python src/seguranca.py verify exemplos/documento.txt publica.pem documento.sig
```

## Testes automatizados

```shell
python -m unittest discover -s tests -v
```

Os testes cobrem hash, divergência após alteração, arquivos PEM, assinatura válida, adulteração, chave pública incorreta e arquivo ausente. Usam somente conteúdo fictício.

## Decisões técnicas e limites

O módulo `cryptography` implementa Ed25519 e os formatos PEM padronizados. SHA-256 isolado detecta diferenças somente quando comparado com uma referência confiável; não comprova autoria. A assinatura é criada diretamente sobre os bytes do arquivo. A chave pública permite validar a assinatura, enquanto a privada deve permanecer sob controle do signatário. Em produção, seria necessário definir armazenamento e rotação de chaves, controle de acesso, identidade do signatário, revogação, carimbo de tempo e cópias de segurança.

## Relatório técnico

Consulte [`docs/RELATORIO_TECNICO.md`](docs/RELATORIO_TECNICO.md). Falta inserir o nome da terceira integrante.

Repositório GitHub: https://github.com/DIONE1000/seguranca-grupo-01
