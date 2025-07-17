# Guia de Setup de Projeto com WSL2, Python e Ambiente Virtual

Este guia explica passo a passo como configurar e continuar um projeto Python com ambiente virtual usando WSL2, desde o clone do repositório até a ativação/desativação do ambiente virtual.

---

## 1. Clonar o Repositório

Abra o terminal no WSL2 e execute:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

## 2. Remover .venv/ se ela veio do repositório

Ambientes virtuais não são portáveis entre máquinas. Se a pasta .venv/ foi clonada junto, remova-a:

```bash
rm -rf .venv/
```

## 3. Criar e Ativar o Ambiente Virtual

Ambientes virtuais não são portáveis entre máquinas. Se a pasta .venv/ foi clonada junto, remova-a:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Instalar as Dependências

Certifique-se de que o arquivo requirements.txt está presente e execute:

```bash
pip install -r requirements.txt
```

## 5. Ignorar .venv/ no Git

Adicione a linha abaixo ao seu arquivo .gitignore:

```bash
.venv/
```

Se a pasta .venv/ já estava sendo rastreada pelo Git, remova-a do controle de versão:

```bash
git rm -r --cached .venv/
git commit -m "Remove .venv do controle de versão"
git push
```

## 6. Ativar e Desativar o Ambiente Virtual

Para ativar:

```bash
source .venv/bin/activate
```

Para desativar:

```bash
deactivate
```
