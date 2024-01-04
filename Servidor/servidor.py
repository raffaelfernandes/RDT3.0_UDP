from socket import *
from os import listdir
from os.path import isfile, join
import hashlib
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

def calcular_checksum(dados):
    # Função para calcular um checksum usando hashlib
    md5 = hashlib.md5()
    md5.update(dados)
    return md5.digest()

# Funções
def envia_arquivo(endereco):
    arquivos = [arquivo for arquivo in listdir("./Servidor/Arquivos") if isfile(join("./Servidor/Arquivos", arquivo))]
    nome_arquivo = ""
    while True:
        data, endereco = serverSocketUDP.recvfrom(BUFFERSIZE)
        mensagem, checksum_recebido = data[:-16], data[-16:]
        if calcular_checksum(mensagem) != checksum_recebido:
            serverSocketUDP.sendto("NACK".encode(), endereco)
            continue
        serverSocketUDP.sendto("ACK".encode(), endereco)
        nome_arquivo = mensagem.decode()
        break

    if nome_arquivo in arquivos:
        serverSocketUDP.sendto("ACK".encode(), endereco)
        with open(("./Servidor/Arquivos/" + nome_arquivo), "rb") as arquivo:
            while (data := arquivo.read(BUFFERSIZE-16)):
                checksum = calcular_checksum(data)
                msg_cksm = data + checksum
                while True:
                    serverSocketUDP.sendto(msg_cksm, endereco)
                    msg, _ = serverSocketUDP.recvfrom(BUFFERSIZE)
                    if msg.decode() == "ACK":
                        break
        print("ARQUIVO ENVIADO")
        serverSocketUDP.sendto(b'', endereco)
    else:
        serverSocketUDP.sendto("NACK".encode(), endereco)

def listar_arquivos(endereco):
    arquivos = arquivos = [arquivo for arquivo in listdir("./Servidor/Arquivos") if isfile(join("./Servidor/Arquivos", arquivo))]
    mensagem = str(arquivos).encode()
    checksum = calcular_checksum(mensagem)
    msg_cksm = mensagem + checksum
    while True:
        serverSocketUDP.sendto(msg_cksm, endereco)
        data, _ = serverSocketUDP.recvfrom(BUFFERSIZE)
        if data.decode() == "ACK":
            break

while True:
    data, endereco = serverSocketUDP.recvfrom(BUFFERSIZE)
    mensagem, checksum_recebido = data[:-16], data[-16:]
    if calcular_checksum(mensagem) != checksum_recebido:
        serverSocketUDP.sendto("NACK".encode(), endereco)
        continue
    serverSocketUDP.sendto("ACK".encode(), endereco)

    opcao = mensagem.decode()
    if opcao == "LISTAR":
        listar_arquivos(endereco)
    elif opcao == "BAIXAR":
        envia_arquivo(endereco)
    elif opcao == "3":
        print("Saindo...")
        break
