import oci
import openpyxl
from datetime import datetime, timedelta
import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType

# Crie um dicionário para armazenar as configurações
config = {
    "user": os.getenv('OCI_USER'),
    "key_content": base64.b64decode(os.getenv('OCI_KEY_CONTENT')).decode('utf-8'),
    "fingerprint": os.getenv('OCI_FINGERPRINT'),
    "tenancy": os.getenv('OCI_TENANCY'),
    "region": os.getenv('OCI_REGION'),
}

# Crie um cliente para o serviço UsageApi
usage_api_client = oci.usage_api.UsageapiClient(config)

# Defina os parâmetros
granularity = "MONTHLY"
group_by = ["service"]
tenant_id = os.getenv('OCI_TENANCY')

# Calcule as datas de início e fim com base na data atual
current_date = datetime.now()
time_usage_ended = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")
time_usage_started = (current_date - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

# Certifique-se de que as datas têm a precisão correta
time_usage_started = time_usage_started.split("T")[0] + "T00:00:00.000Z"
time_usage_ended = time_usage_ended.split("T")[0] + "T00:00:00.000Z"

# Imprima as datas de início e fim
print("Data de início:", time_usage_started)
print("Data de fim:", time_usage_ended)

# Crie o objeto de solicitação
request = oci.usage_api.models.RequestSummarizedUsagesDetails(
    granularity=granularity,
    group_by=group_by,
    tenant_id=tenant_id,
    time_usage_started=time_usage_started,
    time_usage_ended=time_usage_ended
)

# Faça a solicitação
try:
    response = usage_api_client.request_summarized_usages(request)
    
    # Filtrar a resposta para incluir apenas os campos desejados
    filtered_data = []
    total_amount = 0
    for item in response.data.items:
        if item.computed_amount is not None:
            computed_amount = round(item.computed_amount, 2)
            total_amount += computed_amount
        else:
            computed_amount = None

        filtered_item = {
            'service': item.service,
            'computed_amount': computed_amount,
#            'computed_quantity': item.computed_quantity,
            'currency': item.currency
        }
        filtered_data.append(filtered_item)
    
    # Ordenar os dados filtrados por 'Computed Amount' em ordem decrescente
    filtered_data.sort(key=lambda x: x['computed_amount'] if x['computed_amount'] is not None else 0, reverse=True)
    
    # Criar um novo arquivo Excel (.xlsx)
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Adicionar cabeçalhos
    headers = ['Service', 'Computed Amount', 'Currency']
    ws.append(headers)
    
    # Adicionar dados filtrados ao arquivo Excel
    for item in filtered_data:
#        row = [item['service'], item['computed_amount'], item['computed_quantity'], item['currency']]
        row = [item['service'], item['computed_amount'], item['currency']] 
        ws.append(row)
    
    # Adicionar a soma total ao final da coluna 'Computed Amount'
    ws.append(['Total', round(total_amount, 2), ''])

    # Formatação das células
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length

    # Salvar o arquivo Excel
    file_path = 'oci_billing.xlsx'
    wb.save(file_path)
    
    print("Os dados filtrados foram salvos em 'oci_billing.xlsx'")

except oci.exceptions.ServiceError as e:
    print("Ocorreu um erro ao fazer a solicitação:", e)

# Enviar o arquivo por email usando SendGrid

# Definir variáveis do SendGrid e do email 
sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
from_email_address = os.getenv('FROM_EMAIL_ADDRESS')
to_email_address = os.getenv('TO_EMAIL_ADDRESS').split(',')

# Ler o arquivo como bytes e codificar em base64 para o anexo do email 
with open(file_path, 'rb') as f:
   data = f.read()
   f.close()

encoded_file_data = base64.b64encode(data).decode()

attachment = Attachment(
   FileContent(encoded_file_data),
   FileName('oci_billing.xlsx'),
   FileType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
)

# Criar o email
email = Mail(
    from_email=from_email_address,
    to_emails=to_email_address,
    subject='Billing Mensal - OCI Subscription',
    plain_text_content='Anexo, você encontrará o arquivo Excel com os dados referente aos ultimos 30 dias.'
)

email.attachment = attachment

# Enviar o email
try:
    sg = SendGridAPIClient(sendgrid_api_key)
    response = sg.send(email)
    print("Email enviado com sucesso!")
except Exception as e:
    print("Ocorreu um erro ao enviar o email:", e)
