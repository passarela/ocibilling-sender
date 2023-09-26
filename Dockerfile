# Use uma imagem base do Python
FROM python:3.8-slim-buster

# Defina o diretório de trabalho
WORKDIR /app

# Instale as dependências necessárias
RUN pip install oci openpyxl sendgrid

# Copie o script Python para o contêiner
COPY . .

# Execute o script Python
CMD ["python", "./oci-cli.py"]
#CMD ["sleep", "infinity"]