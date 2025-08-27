🧱 Passo a passo para criar um ambiente virtual com venv

1. Abra o terminal no diretório do seu projeto.

2. Crie o ambiente virtual com o seguinte comando:

```python
python3 -m venv .venv

```

3. Ative o ambiente virtual:

- WSL / Linux:

```python
source .venv/bin/activate

```

4. Atualizar pip:

```python
pip install --upgrade pip

```

5. Instalar dependências:

```python
pip install -r requirements.txt

```
