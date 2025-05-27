# Usa uma imagem leve do Python
FROM python:3.9-slim

# Instala o Docker dentro do container
RUN apt-get update && apt-get install -y --no-install-recommends docker.io && \
    rm -rf /var/lib/apt/lists/*  # Limpa arquivos temporários para manter a imagem leve

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas o arquivo de dependências primeiro (melhora o cache do Docker)
COPY requirements.txt ./

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos para o container
COPY . .

# Comando de inicialização do serviço
CMD ["python", "scaler.py"]
