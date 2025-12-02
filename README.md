# PLN_ArtigosCientificos

Programa de Processamento de Linguagem Natural (PLN) que analisa artigos científicos em PDF, extraindo informações relevantes de forma automática e realizando análise comparativa dos resultados em múltiplos artigos.

### Instruções para rodar o programa

```bash
git clone https://github.com/lissakawasaki/PLN_ArtigosCientificos.git
cd PLN_ArtigosCientificos

2. Configurar o Ambiente Virtual

# Cria o ambiente virtual
python3 -m venv venv

# Ativa o ambiente
source venv/bin/activate

3. Instalar Dependências

pip freeze > requirements.txt
pip install -r requirements.txt

4. Preparar Pasta de Artigos

Crie a pasta articles/ e adicione seus arquivos PDF nela:

mkdir articles

5. Executar o Programa

python main.py
