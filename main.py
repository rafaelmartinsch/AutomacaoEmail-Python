import pymysql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from prettytable import PrettyTable
from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

# Função para conectar ao banco de dados MySQL
def get_lista_produtos():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    try:
        with connection.cursor() as cursor:
            # Query para buscar produtos com qtd = 0
            sql = "SELECT * FROM produtos WHERE qtd = 0"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()

# Função para enviar e-mail com a lista de produtos
def send_email(products):
    # Configurações do e-mail
    sender_email = os.getenv('SMTP_USER')
    receiver_email = os.getenv('GERENTE_EMAIL')
    titulo = "Alerta: Produtos com estoque zerado"
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # Criando a tabela de produtos
    table = PrettyTable(['Produto', 'Quantidade'])
    for product in products:
        table.add_row([product[0], product[1]])
    
    # Criando o corpo do e-mail
    body = f"Prezado Gerente,\n\nOs seguintes produtos estão com estoque zerado e precisam de reposição:\n\n"
    body += table.get_string()
    body += "\n\nPor favor, providencie a reposição do estoque."

    # Montando o e-mail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = titulo
    msg.attach(MIMEText(body, 'plain'))

    # Enviando o e-mail
    server = None
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {str(e)}")
    finally:
        if server:
            server.quit()

# Função principal
if __name__ == "__main__":
    produtos = get_lista_produtos()
    if produtos:
        print(produtos)
        send_email(produtos)
    else:
        print("Não há produtos com estoque zerado.")
