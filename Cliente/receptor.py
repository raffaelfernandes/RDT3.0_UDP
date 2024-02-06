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
PORT_ENVIO = 51000
PORT_ESCUTA = PORT_ENVIO + 1
PORT_CONECTADO = PORT_ESCUTA + 1
PORT = 52000
ADDR = (HOST, PORT)
BUFFERSIZE = 1024

# ENVIA NA PORTA 51000
# ESCUTA NA PORTA 51001

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

def receber_dados():
    global seq
    global clienteConexao
    data, _ = clienteConexao.recvfrom(BUFFERSIZE)
    if (data == "ENVIAR".encode()):
        return
    clientUnpacker = Struct('I 1004s 16s')
    seq_pct, conteudo, checksum_recebido = clientUnpacker.unpack(data)

    seq_num = 1 if seq else 0

    ACK_packer = Struct('I 1004s 16s')
    ACK = ACK_packer.pack(seq_num, 'ACK'.encode(), bytes.fromhex(calcular_checksum('ACK'.encode())))
    #NACK = ACK_NACK_packer.pack('NACK'.encode(), bytes.fromhex(calcular_checksum('NACK'.encode())))

    checksum_calculado = bytes.fromhex(calcular_checksum(conteudo.rstrip(b'\x00')))

    #cksm_pack = Struct('16s')
    #cksm_pack.pack(checksum_calculado)
    if(checksum_calculado != checksum_recebido or seq_num != seq_pct):
        if seq_num == 1:
            seq_num = 0
        else:
            seq_num = 1
        print("\nALERTA: A mensagem está corrompida ou duplicada. Aguardando reenvio...")
        print(f"Enviando ACK para {seq_num}...")
    else:
        seq = not seq
        print(f"\nA mensagem está OK! Enviando ACK para {seq_num}...")
        conteudo = conteudo.rstrip(b'\x00')
        print(f"\n\nConteúdo recebido: {conteudo.decode('utf-8')}")
        print()
    
    ACK = ACK_packer.pack(seq_num, 'ACK'.encode(), bytes.fromhex(calcular_checksum('ACK'.encode())))
    clientSocketUDP.sendto("ENVIAR".encode(), ADDR)
    clientSocketUDP.sendto(ACK, ADDR)
    
    return

def escutar_porta(porta):
    global clienteConexao
    clienteConexao = socket(AF_INET, SOCK_DGRAM)
    clienteConexao.bind(('localhost', porta))
    while True:
        dados, endereco = clienteConexao.recvfrom(1024)
        if dados == "ENVIAR".encode():
            receber_dados()
            #interface()
        if dados == "CONN".encode():
            print("Conectado ao servidor!")
        continue

thread_escuta = threading.Thread(target=escutar_porta, args=(PORT_ESCUTA,))
thread_escuta.start()

def interface():
    menu()
    opcao = input()
    if opcao == "1":
        clientSocketUDP.sendto('CONN'.encode(), ADDR)
        time.sleep(3)
    elif opcao == "3":
        clientSocketUDP.sendto("3".encode(), ADDR)
        clientSocketUDP.close()
        return
    else:
        print("Opção inválida!")
        interface()

interface()