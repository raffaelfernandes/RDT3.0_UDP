from socket import *
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
PORT_CONECTADO = PORT_ESCUTA + 1
PORT = 52000
ADDR = (HOST, PORT)
BUFFERSIZE = 1024

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
    receber_ack_ou_nack(pacote)

        

def receber_ack_ou_nack(pacote):
    global socket_conectado
    global seq
    socket_conectado = socket(AF_INET, SOCK_DGRAM)
    socket_conectado.bind(('localhost', PORT_CONECTADO))
    while True:
        dados, _ = socket_conectado.recvfrom(BUFFERSIZE)
        if (dados == "ENVIAR".encode()):
            dados, endereco = socket_conectado.recvfrom(BUFFERSIZE)
            clientUnpacker = Struct('1008s 16s')
            conteudo, checksum_recebido = clientUnpacker.unpack(dados)
            if(bytes.fromhex(calcular_checksum(conteudo.rstrip(b'\x00'))) != checksum_recebido) or conteudo.rstrip(b'\x00') == "NACK".encode():
                clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
                clientSocketUDP.sendto(pacote, ADDR)
            else:
                if(conteudo.rstrip(b'\x00') == "ACK".encode()):
                    seq = not seq
                    break


def receber_dados():
    global seq
    global clienteConexao
    data, _ = clienteConexao.recvfrom(BUFFERSIZE)
    clientUnpacker = Struct('I 1004s 16s')
    seq_pct, conteudo, checksum_recebido = clientUnpacker.unpack(data)

    seq_num = 1 if seq else 0

    ACK_NACK_packer = Struct('1008s 16s')
    ACK = ACK_NACK_packer.pack('ACK'.encode(), bytes.fromhex(calcular_checksum('ACK'.encode())))
    NACK = ACK_NACK_packer.pack('NACK'.encode(), bytes.fromhex(calcular_checksum('NACK'.encode())))

    checksum_calculado = bytes.fromhex(calcular_checksum(conteudo.rstrip(b'\x00')))

    #cksm_pack = Struct('16s')
    #cksm_pack.pack(checksum_calculado)

    if(checksum_calculado != checksum_recebido):
        clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
        clientSocketUDP.sendto(NACK, ADDR)
    else:
        if seq_pct != seq_num:
            clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
            clientSocketUDP.sendto(ACK, ADDR)
        else:
            clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
            clientSocketUDP.sendto(ACK, ADDR)
            seq = not seq
            conteudo = conteudo.rstrip(b'\x00')
            print(f"\n\nConteúdo recebido: {conteudo.decode('utf-8')}")
            print()
            return

def escutar_porta(porta):
    global clienteConexao
    global new_menu
    clienteConexao = socket(AF_INET, SOCK_DGRAM)
    clienteConexao.bind(('localhost', porta))
    while True:
        dados, endereco = clienteConexao.recvfrom(1024)
        if dados.decode() == "ENVIAR":
            receber_dados()
        if dados.decode() == "CONN":
            print("Conectado ao servidor!")
        continue

thread_escuta = threading.Thread(target=escutar_porta, args=(PORT_ESCUTA,))
thread_escuta.start()

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
        return
    else:
        print("Opção inválida!")
        interface()

interface()