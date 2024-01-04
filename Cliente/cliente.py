from socket import *
import hashlib
import sys
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
clientSocketUDP = socket(AF_INET, SOCK_DGRAM)

# Funções
def menu():
    print("\n"+"-"*20 + "MENU" + "-"*20+'\n')
    print("1 - Listar arquivos")
    print("2 - Baixar arquivo")
    print("3 - Sair")
    print("Digite a opção desejada: ", end="")

def calcular_checksum(dados):
    # Função para calcular um checksum usando hashlib
    md5 = hashlib.md5()
    md5.update(dados)
    return md5.digest()

def verifica_servidor():
    # Envia mensagem para o servidor
    clientSocketUDP.sendto("1".encode(), ADDR)

    # Define um tempo limite de 5 segundos
    clientSocketUDP.settimeout(5.0)

    try:
        # Recebe resposta do servidor
        data, _ = clientSocketUDP.recvfrom(BUFFERSIZE)
        if data.decode() == "1":
            clientSocketUDP.settimeout(None)
            return True
    except TimeoutError:
        return False
    except Exception as e:
        print(f"Erro: {e}")

def listarArquivos():
    # Envia mensagem para o servidor
    mensagem = "LISTAR".encode()
    checksum = calcular_checksum(mensagem)
    msg_cksm = mensagem + checksum
    while True:
        clientSocketUDP.sendto(msg_cksm, ADDR)

        # Recebe ACK ou NACK do servidor
        data, _ = clientSocketUDP.recvfrom(BUFFERSIZE)
        if data.decode() == "ACK":
            break

    # Recebe resposta do servidor
    while True:
        data, _ = clientSocketUDP.recvfrom(BUFFERSIZE)
        mensagem, checksum_recebido = data[:-16], data[-16:]
        if calcular_checksum(mensagem) != checksum_recebido:
            clientSocketUDP.sendto("NACK".encode(), ADDR)
            continue
        clientSocketUDP.sendto("ACK".encode(), ADDR)
        break

    print("Arquivos disponíveis:")
    print(mensagem.decode())

def baixarArquivo():
    mensagem = "BAIXAR".encode()
    checksum = calcular_checksum(mensagem)
    msg_cksm = mensagem + checksum
    while True:
        clientSocketUDP.sendto(msg_cksm, ADDR)

        # Recebe ACK ou NACK do servidor
        data, _ = clientSocketUDP.recvfrom(BUFFERSIZE)
        if data.decode() == "ACK":
            break

    # Envia nome do arquivo para o servidor
    nome_arquivo = input("Digite o nome do arquivo: ")
    mensagem = nome_arquivo.encode()
    checksum = calcular_checksum(mensagem)
    msg_cksm = mensagem + checksum
    while True:
        clientSocketUDP.sendto(msg_cksm, ADDR)

        # Recebe ACK ou NACK do servidor
        data, _ = clientSocketUDP.recvfrom(BUFFERSIZE)
        if data.decode() == "ACK":
            break

    # Recebe resposta do servidor
    data, _ = clientSocketUDP.recvfrom(BUFFERSIZE)
    if data.decode() == "NACK":
        print("\n"+"ARQUIVO NÃO ENCONTRADO")
    else:
        # Cria arquivo
        with open(nome_arquivo, "wb") as arquivo:
            # Recebe dados do servidor
            while True:
                data, server = clientSocketUDP.recvfrom(BUFFERSIZE)
                if not data:
                    break
                mensagem, checksum_recebido = data[:-16], data[-16:]
                if calcular_checksum(mensagem) != checksum_recebido:
                    clientSocketUDP.sendto("NACK".encode(), server)
                    continue
                clientSocketUDP.sendto("ACK".encode(), server)
                arquivo.write(mensagem)
        print("\nARQUIVO RECEBIDO")

while True:
    menu()
    opcao = input()
    if opcao == "1":
        listarArquivos()
    elif opcao == "2":
        baixarArquivo()
    elif opcao == "3":
        clientSocketUDP.sendto("3".encode(), ADDR)
        clientSocketUDP.close()
        break
    else:
        print("Opção inválida!")