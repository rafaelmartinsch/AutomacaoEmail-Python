from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import mysql
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv() # Carregar arquivo de configuração

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

# Enviar e-mail com tabela HTML estilizada
def send_email(produtos):
    destinatario = os.getenv("GERENTE_EMAIL")
    remetente = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")
    servidor = os.getenv("SMTP_SERVER")
    porta = os.getenv("SMTP_PORT")
    titulo = "Alerta: Produtos com estoque zerado"
    
    # Criando a tabela em HTML
    table = '''
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background-color: #9999ff;">
                <th style="padding: 8px;">Produto</th>
                <th style="padding: 8px;">Quantidade</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for produto in produtos:
        table += f'''
        <tr style="background-color: #f2f2f2;">
            <td style="padding: 8px; text-align: center;">{produto[1]}</td>
            <td style="padding: 8px; text-align: center;">{produto[3]}</td>
        </tr>
        '''
    
    table += '''
        </tbody>
    </table>
    '''

    corpo = f'''
    <html>
    <body>
        <p>Prezado gerente,</p>
        <p>Os seguintes produtos estão com estoque zerado:</p>
        {table}
        <p>Por favor, providencie a reposição!</p>
    </body>
    </html>
    '''

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = titulo
    msg.attach(MIMEText(corpo, 'html'))

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
