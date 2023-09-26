# OCI Billing - Sender

Automação simples em Python com o objetivo de recuperar via OCI API os custos categorizados por serviço nos ultimos 30 dias. Após gerar está integrado com bibliotecas do Sendgrid para envio de e-mail.

## Docker build

~~~~

git clone https://github.com/passarela/ocibilling-sender.git

docker build . -t repo/imagem:tag

~~~~

## Definir variáveis

~~~~
nano .env
OCI_USER=<TENANCY OCID>
OCI_FINGERPRINT=<FINGERPRINT>
OCI_KEY_CONTENT=<OCI PRIV KEY EM BASE64>
OCI_REGION=<REGIAO>
FROM_EMAIL_ADDRESS=<EMAIL AUTORIZADO SENDGRID>
TO_EMAIL_ADDRESS=<DESTINATARIOS SEPARADOS POR VIRGULA>
SENDGRID_API_KEY=<SENDGRID APIKEY>
~~~~

## Iniciar Container

~~~~
docker run --env-file ./.env repo/imagem:tag 
~~~~
