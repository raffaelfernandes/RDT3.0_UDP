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

usuarios = []

def calcular_checksum(dados):
    # Função para calcular um checksum usando hashlib
    md5 = hashlib.md5()
    md5.update(dados)
    return md5.digest()

def menu_envio():
    print("\n"+"-"*20 + "MENU" + "-"*20+'\n')
    print("1 - Enviar pacote sem alterações")
    print("2 - Modificar pacote")
    print("3 - Causar perda do pacote")
    print("4 - Enviar pacote com atraso")
    print("Digite a opção desejada: ", end="")

# Funções
def envia_dados(endereco):
    
    dados, _ = serverSocketUDP.recvfrom(BUFFERSIZE)
    seq_num, conteudo, checksum = dados[:2], dados[2:-2], dados[-2:]

    menu_envio()
    opcao = input()
    if opcao == "1":
        print("Enviando pacote sem alterações...")
        envio_normal(dados)
    elif opcao == "2":
        print("Modificando pacote...")
        num_bits = int(input("Digite a quantidade de bits a serem modificados: "))
        novo_conteudo = modificar_bits(conteudo, num_bits)
        nova_msg = seq_num + novo_conteudo + checksum
        envio_normal(nova_msg)
    elif opcao == "3":
        print("Causando perda do pacote...")
        envio_perda()
    elif opcao == "4":
        print("Enviando pacote com atraso...")
        tempo_atraso = int(input("Digite o tempo (em segundos) de atraso: "))
        envia_pacote_atraso(conteudo, tempo_atraso)
    
    def envio_normal(dados):
        for usuario in usuarios:
            if usuario == endereco:
                continue
            serverSocketUDP.sendto('ENVIAR', usuario)
            serverSocketUDP.sendto(dados, usuario)

    def modificar_bits(mensagem, num_bits):
        bits = list(mensagem)
        tamanho_mensagem = len(bits)
        for _ in range(num_bits):
            indice_bit = random.randint(0, tamanho_mensagem - 1)
            bits[indice_bit] = '1' if bits[indice_bit] == '0' else '0'
        return ''.join(bits)
    
    def envio_perda():
        for usuario in usuarios:
            if usuario == endereco:
                continue
            serverSocketUDP.sendto('ENVIAR', usuario)

    def envia_pacote_atraso(dados, tempo_atraso):
        for usuario in usuarios:
            if usuario == endereco:
                continue
            serverSocketUDP.sendto('ENVIAR', usuario)
            time.sleep(tempo_atraso)
            serverSocketUDP.sendto(dados, usuario)

while True:
    data, endereco = serverSocketUDP.recvfrom(BUFFERSIZE)
    if endereco not in usuarios:
        usuarios.append(endereco)
    print(usuarios)
    
    opcao = data.decode()
    if opcao == "ENVIAR":
        envia_dados(endereco)
    elif opcao == "3":
        print("Saindo...")
        break
