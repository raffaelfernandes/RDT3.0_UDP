from socket import *
from os import listdir
from os.path import isfile, join
import hashlib
import os
import time
import threading
import random
from struct import Struct

# Constantes
HOST = 'localhost'
PORT = 52000
ADDR = (HOST, PORT)
BUFFERSIZE = 1024
seq = False

# Variáveis globais
serverSocketUDP = socket(AF_INET, SOCK_DGRAM)
serverSocketUDP.bind(ADDR)
print("Servidor iniciado!\n")

usuarios = []

def calcular_checksum(dados):
    # Função para calcular um checksum usando hashlib
    md5 = hashlib.md5()
    md5.update(dados)
    return md5.hexdigest()

def menu_envio():
    print("\n"+"-"*20 + "MENU" + "-"*20+'\n')
    print("1 - Enviar pacote sem alterações")
    print("2 - Modificar pacote")
    print("3 - Causar perda do pacote")
    print("4 - Enviar pacote com atraso")
    print("Digite a opção desejada: ", end="")

# Funções
def envia_dados(endereco):
    global seq

    def envio_normal(dados, ack_or_nack):
        for usuario in usuarios:
            if usuario == endereco:
                continue
            if ack_or_nack:
                end, porta = usuario
                usuario = (end, porta + 1)
                serverSocketUDP.sendto("ENVIAR".encode(), usuario)
                serverSocketUDP.sendto(dados, usuario)
            else:
                serverSocketUDP.sendto("ENVIAR".encode(), usuario)
                serverSocketUDP.sendto(dados, usuario)

    def modificar_bits(mensagem, num_bits):
        bits = list(mensagem)
        tamanho_mensagem = len(bits)
        for _ in range(num_bits):
            indice_bit = random.randint(0, tamanho_mensagem - 1)
            bits[indice_bit] = '1' if bits[indice_bit] == '0' else '0'
        return ''.join(str(bit) for bit in bits)
    
    def envio_perda():
        for usuario in usuarios:
            if usuario == endereco:
                continue
            serverSocketUDP.sendto('ENVIAR'.encode(), usuario)

    def envia_pacote_atraso(dados, tempo_atraso):
        for usuario in usuarios:
            if usuario == endereco:
                continue
            serverSocketUDP.sendto('ENVIAR'.encode(), usuario)
            time.sleep(tempo_atraso)
            serverSocketUDP.sendto(dados, usuario)
    
    
    ack_or_nack = True

    dados, _ = serverSocketUDP.recvfrom(BUFFERSIZE)
    ACK_NACK_packer = Struct('1008s 16s')
    conteudo, checksum = ACK_NACK_packer.unpack(dados)
    conteudo = conteudo.rstrip(b'\x00')
    ACK = b'ACK'
    NACK = b'NACK'
    if not (conteudo == ACK or conteudo == NACK):
        data_packet = Struct('I 1004s 16s')
        seq_num, conteudo, checksum = data_packet.unpack(dados)
        ack_or_nack = False

    menu_envio()
    opcao = input()
    if opcao == "1":
        print("Enviando pacote sem alterações...")
        envio_normal(dados, ack_or_nack)
        print("Pacote Enviado!")
    elif opcao == "2":
        print("Modificando pacote...")
        num_bits = int(input("Digite a quantidade de bits a serem modificados: "))
        novo_conteudo = modificar_bits(conteudo, num_bits)
        if ack_or_nack:
            nova_msg = ACK_NACK_packer.pack(novo_conteudo.encode(), checksum)
        else:
            nova_msg = data_packet.pack(seq_num, novo_conteudo.encode(), checksum)
        envio_normal(nova_msg, ack_or_nack)
    elif opcao == "3":
        print("Causando perda do pacote...")
        envio_perda()
    elif opcao == "4":
        print("Enviando pacote com atraso...")
        tempo_atraso = int(input("Digite o tempo (em segundos) de atraso: "))
        envia_pacote_atraso(conteudo, tempo_atraso)

while True:
    data, tupla = serverSocketUDP.recvfrom(BUFFERSIZE)
    end_envio, porta_envio = tupla
    endereco = (end_envio, porta_envio + 1)

    if (endereco) not in usuarios:
        usuarios.append(endereco)
    print(usuarios)
    
    opcao = data.decode('utf-8', 'ignore')
    if opcao == "ENVIAR":
        envia_dados(endereco)
    elif opcao == "CONN":
        serverSocketUDP.sendto("CONN".encode(), endereco)
    elif opcao == "3":
        print("Saindo...")
        break
    else:
        continue
