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

# SEQ = TAM 2 BYTES
# CHECKSUM = TAM 2 BYTES
# CONTEÚDO = TAM (SOBRAR) BYTES

# Variáveis globais
clientSocketUDP = socket(AF_INET, SOCK_DGRAM)
seq = False

# Funções
def menu():
    print("\n"+"-"*20 + "MENU" + "-"*20+'\n')
    print("1 - Enviar pacotes")
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

def enviar_pacote():
    clientSocketUDP.sendto("ENVIAR".encode(), ADDR)

    conteudo = input(" Digite o conteúdo da mensagem: ")
    conteudo = conteudo.encode()

    msg = str(seq).encode() + conteudo + calcular_checksum(conteudo)
    while True:
        clientSocketUDP.sendto(msg, ADDR)

        data, endereco = clientSocketUDP.recvfrom(BUFFERSIZE)
        seq, conteudo, checksum_recebido = data[:2], data[2:-2], data[-2:]
        if(calcular_checksum(conteudo) != checksum_recebido) or conteudo.decode() != "NACK":
            clientSocketUDP.sendto(msg, ADDR)
        else:
            if(conteudo.decode() == "ACK"):
                seq = not seq
                break
            else:
                continue

def receber_dados():
    data, endereco = clientSocketUDP.recvfrom(BUFFERSIZE)
    seq_pct, conteudo, checksum_recebido = data[:2], data[2:-2], data[-2:]

    if(calcular_checksum(conteudo) != checksum_recebido):
        retorno = 'NACK' + calcular_checksum('NACK')
        clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
        clientSocketUDP.sendto(retorno, ADDR)
    else:
        if seq_pct != seq:
            retorno = 'ACK' + calcular_checksum('ACK')
            clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
            clientSocketUDP.sendto(retorno, ADDR)
        else:
            retorno = 'ACK' + calcular_checksum('ACK')
            clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
            clientSocketUDP.sendto(retorno, ADDR)
            seq = not seq

def escutar_porta(porta):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente.bind(('localhost', porta))
    while True:
        dados, endereco = cliente.recvfrom(1024)
        if dados.decode() == "ENVIAR":
            receber_dados()

thread_escuta = threading.Thread(target=escutar_porta, args=(PORT+1,))
thread_escuta.start()

while True:
    menu()
    opcao = input()
    if opcao == "1":
        enviar_pacote()
    elif opcao == "3":
        clientSocketUDP.sendto("3".encode(), ADDR)
        clientSocketUDP.close()
        break
    else:
        print("Opção inválida!")