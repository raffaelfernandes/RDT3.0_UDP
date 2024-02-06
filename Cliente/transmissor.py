from socket import *
import select
import hashlib
import sys
import os
import time
import threading
import random
from struct import Struct

# Constantes
HOST = 'localhost'
PORT_ENVIO = 50000
PORT_ESCUTA = PORT_ENVIO + 1
PORT = 52000
ADDR = (HOST, PORT)
BUFFERSIZE = 1024
timeout = 25

# ENVIA NA PORTA 50000
# ESCUTA NA PORTA 50001

# SEQ = TAM 2 BYTES
# CHECKSUM = TAM 2 BYTES
# CONTEÚDO = TAM (SOBRAR) BYTES

# Variáveis globais
clientSocketUDP = socket(AF_INET, SOCK_DGRAM)
clientSocketUDP.bind(('localhost', PORT_ENVIO))
global clienteConexao
global socket_conectado
# Definindo variável seq global:
seq = False
new_menu = True
timer = None
temporizador_estourou = False
comunicacao = False

# Funções
def menu():
    print("\n"+"-"*20 + "MENU" + "-"*20+'\n')
    print("1 - Conectar ao servidor")
    print("2 - Enviar mensagem")
    print("3 - Sair")
    print("Digite a opção desejada: ", end="")

def calcular_checksum(dados):
    # Função para calcular um checksum usando hashlib
    md5 = hashlib.md5()
    md5.update(dados)
    return md5.hexdigest()

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
    global seq
    clientSocketUDP.sendto("ENVIAR".encode(), ADDR)

    # definindo um packet format para num_seq, conteúdo e checksum:
    packet_format = Struct('I 1004s 16s')

    conteudo = input("Digite o conteúdo da mensagem: ")
    conteudo = conteudo.encode()

    if seq:
        valores = (1, conteudo, bytes.fromhex(calcular_checksum(conteudo)))
        pacote = packet_format.pack(*valores)
    else:
        valores = (0, conteudo, bytes.fromhex(calcular_checksum(conteudo)))
        pacote = packet_format.pack(*valores)

    clientSocketUDP.sendto(pacote, ADDR)
    receber_ack(pacote)

def timeout_timer(timeout, pacote):
    global temporizador_estourou
    global comunicacao

    while comunicacao == False:
        temporizador_estourou = False
        time.sleep(timeout)
        if comunicacao:
            break
        temporizador_estourou = True
        clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
        clientSocketUDP.sendto(pacote, ADDR)
    
    return

global stop_event

def start_timer(timeout, pacote):
    global timer
    global temporizador_estourou
    timer = threading.Thread(target=timeout_timer, args=(timeout, pacote))
    timer.start()
        
def receber_ack(pacote):
    global socket_conectado
    global seq
    global comunicacao
    global timer

    socket_conectado = socket(AF_INET, SOCK_DGRAM)
    socket_conectado.bind(('localhost', PORT_ESCUTA))

    comunicacao = False
    start_timer(timeout, pacote)

    while True:
        dados, _ = socket_conectado.recvfrom(BUFFERSIZE)
        if (dados == "ENVIAR".encode()):
            dados, _ = socket_conectado.recvfrom(BUFFERSIZE)
            if(dados == "ENVIAR".encode()):
                continue
            clientUnpacker = Struct('I 1004s 16s')
            if seq:
                seq_num = 1
            else:
                seq_num = 0
            seq_ack, conteudo, checksum_recebido = clientUnpacker.unpack(dados)
            if(bytes.fromhex(calcular_checksum(conteudo.rstrip(b'\x00'))) != checksum_recebido) or seq_ack != seq_num:
                pass
            else:
                seq = not seq
                print(f'\n ACK para {seq_num} Recebido!')
                comunicacao = True
                break
        else:
            clientUnpacker = Struct('I 1004s 16s')
            if seq:
                seq_num = 1
            else:
                seq_num = 0
            seq_ack, conteudo, checksum_recebido = clientUnpacker.unpack(dados)
            if(bytes.fromhex(calcular_checksum(conteudo.rstrip(b'\x00'))) != checksum_recebido) or seq_ack != seq_num:
                pass
            else:
                seq = not seq
                print(f'\n ACK para {seq_num} Recebido!')
                comunicacao = True
                break


def interface():
    menu()
    opcao = input()
    if opcao == "1":
        clientSocketUDP.sendto('CONN'.encode(), ADDR)
        time.sleep(1)
        interface()
    if opcao == "2":
        enviar_pacote()
        interface()
    elif opcao == "3":
        clientSocketUDP.sendto("3".encode(), ADDR)
        clientSocketUDP.close()
        return 1
    else:
        print("Opção inválida!")
        interface()

while True:
    ret = interface()
    if ret == 1:
        break