# Usa uma imagem Python oficial como base
FROM python:3.13-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Instala dependências a nível de sistema (necessário para compilar pacotes como infomap)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt ./
COPY main/requirements.txt ./main/

# Instala as dependências de ambos os arquivos
# O --no-cache-dir é uma boa prática para manter a imagem menor
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r main/requirements.txt

# Instala as dependências adicionais que descobrimos durante a execução
RUN pip install --no-cache-dir seaborn csvkit infomap python-louvain

# Copia todo o código do projeto para o diretório de trabalho no container
COPY . .

# Expõe a porta do Streamlit (dashboard) para que possamos acessá-la de fora
EXPOSE 8501

# Comando padrão para iniciar o container (abre um terminal bash)
# Isso nos dará flexibilidade para rodar o pipeline ou o dashboard manualmente
CMD ["bash"]
