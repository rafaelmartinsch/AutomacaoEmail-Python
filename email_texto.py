from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import mysql
import mysql.connector
import os
from dotenv import load_dotenv
from prettytable import PrettyTable

load_dotenv() #carregar arquivo de configuração
#retorna list de produtos zerados
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
        resultado=cursor.fetchall()
        return resultado
    except mysql.connector.Error as e:
        print(f"Erro ao conectar com o BD:{e}")
    finally:
        conexao.close()
        cursor.close()

def send_email(produtos):
    destinatario =  os.getenv("GERENTE_EMAIL")
    remetente = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")
    servidor = os.getenv("SMTP_SERVER")
    porta = os.getenv("SMTP_PORT")
    titulo = "Alerta: Produtos com estoque zerados"
    
    table =  PrettyTable(['Produto','Quantidade'])
    for produto in produtos:
        table.add_row([produto[1], produto[3]])
    
    corpo = "Prezado gerente. os seguintes produtos estão com estoque zerado:"
    corpo += "\n\n por favor providencie a reposição!"
    corpo += table.get_string()
    
    msg =  MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = titulo
    msg.attach(MIMEText(corpo, 'plain'))
    
    server = None
    try:
        server=smtplib.SMTP(servidor, porta)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente,destinatario,msg.as_string())
        print("E-mail enviado")
    except Exception as e:
        print("Erro ao enviar: ", e)
    finally:
        if server:
            server.quit()

#main    
send_email(listaProdutos())
