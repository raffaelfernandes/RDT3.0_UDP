from socket import *
from os import listdir
from os.path import isfile, join
import os
import time
import threading
import random

# Constantes
HOST = 'localhost'
PORT = 50000
ADDR = (HOST, PORT)
BUFFERSIZE = 1024

# Variáveis globais
serverSocketUDP = socket(AF_INET, SOCK_DGRAM)
serverSocketUDP.bind(ADDR)
print("Servidor iniciado!\n")

# Funções
def envia_arquivo(endereco):
    arquivos = [arquivo for arquivo in listdir("./Servidor/Arquivos") if isfile(join("./Servidor/Arquivos", arquivo))]
    data, _ = serverSocketUDP.recvfrom(BUFFERSIZE)
    nome_arquivo = data.decode()
    if nome_arquivo in arquivos:
        serverSocketUDP.sendto("ARQUIVO ENCONTRADO".encode(), endereco)
        with open(("./Servidor/Arquivos/" + nome_arquivo), "rb") as arquivo:
            while (data := arquivo.read(BUFFERSIZE)):
                serverSocketUDP.sendto(data, endereco)
        print("ARQUIVO ENVIADO")
        serverSocketUDP.sendto(b'', endereco)
    else:
        serverSocketUDP.sendto("ARQUIVO NAO ENCONTRADO".encode(), endereco)

def listar_arquivos(endereco):
    arquivos = arquivos = [arquivo for arquivo in listdir("./Servidor/Arquivos") if isfile(join("./Servidor/Arquivos", arquivo))]
    serverSocketUDP.sendto(str(arquivos).encode(), endereco)

while True:
    data, endereco = serverSocketUDP.recvfrom(BUFFERSIZE)
    opcao = data.decode()
    if opcao == "LISTAR":
        listar_arquivos(endereco)
    elif opcao == "BAIXAR":
        envia_arquivo(endereco)
    elif opcao == "3":
        print("Saindo...")
        break
