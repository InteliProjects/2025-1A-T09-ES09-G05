# Usa uma imagem leve do Python
FROM python:3.9

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas as dependências primeiro (melhora o cache do Docker)
COPY requirements.txt ./ 

# Instala as dependências do Locust e do Prometheus Client
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação
COPY . .

# Expondo as portas necessárias
EXPOSE 8089  
EXPOSE 9646  


# Copia o script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN apt-get update && apt-get install -y dos2unix && \
    dos2unix /entrypoint.sh && \
    chmod +x /entrypoint.sh
# ! Copia o script de entrada (no windows)
# COPY entrypoint.sh /entrypoint.sh
# RUN apt-get update && apt-get install -y dos2unix && \
#     dos2unix /entrypoint.sh && \
#     chmod +x /entrypoint.sh


# Usa o script de entrada para iniciar múltiplos processos
CMD ["/entrypoint.sh"]