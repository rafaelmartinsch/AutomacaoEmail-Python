from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import mysql
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Carregar arquivo de configuração

# Retorna lista de produtos zerados
def listaProdutos():
    conexao = None
    try:
        conexao = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        print("Conectado!")
        
        cursor = conexao.cursor()
        SQL = "SELECT * FROM produto WHERE qtd=0"
        cursor.execute(SQL)
        resultado = cursor.fetchall()
        return resultado
    except mysql.connector.Error as e:
        print(f"Erro ao conectar com o BD: {e}")
    finally:
        if conexao:
            conexao.close()
        if cursor:
            cursor.close()

# Enviar e-mail com o PDF em anexo
def send_email(produtos):
    destinatario = os.getenv("GERENTE_EMAIL")
    remetente = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")
    servidor = os.getenv("SMTP_SERVER")
    porta = os.getenv("SMTP_PORT")
    titulo = "Alerta: Produtos com estoque zerado"
    
    # Corpo do e-mail
    corpo = '''
    <html>
    <body>
        <p>Prezado gerente,</p>
        <p>Segue o relatório de estoque em anexo.</p>
        <p>Por favor, providencie a reposição dos produtos com estoque zerado!</p>
    </body>
    </html>
    '''

    # Configurando a mensagem do e-mail
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = titulo
    msg.attach(MIMEText(corpo, 'html'))

    # Anexando o arquivo PDF
    caminho_pdf = "src/relatorio.pdf"
    with open(caminho_pdf, "rb") as f:
        anexo = MIMEBase('application', 'octet-stream')
        anexo.set_payload(f.read())
        encoders.encode_base64(anexo)
        anexo.add_header('Content-Disposition', f'attachment; filename=relatorio.pdf')
        msg.attach(anexo)

    # Envio do e-mail
    server = None
    try:
        server = smtplib.SMTP(servidor, porta)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        print("E-mail enviado")
    except Exception as e:
        print("Erro ao enviar: ", e)
    finally:
        if server:
            server.quit()

# Main
send_email(listaProdutos())
