#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo Principal
--------------
Este é o ponto de entrada da aplicação de varredura de rede.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import platform

# Verifica se estamos no Windows
if platform.system() != "Windows":
    print("Aviso: Esta aplicação foi projetada para Windows. Algumas funcionalidades podem não funcionar corretamente.")

# Verifica se os módulos necessários estão disponíveis
try:
    # Importa os módulos da aplicação
    from gui import NetworkScannerGUI
    from network_scanner import NetworkScanner
    from data_manager import DataManager
except ImportError as e:
    # Exibe uma mensagem de erro e sai
    print(f"Erro ao importar módulos: {e}")
    print("Verifique se todos os arquivos estão no mesmo diretório.")
    sys.exit(1)

# Verifica se as bibliotecas necessárias estão instaladas
try:
    import socket
    import threading
    import subprocess
    import ipaddress
    from PIL import Image, ImageTk, ImageDraw
    
    # Tenta importar scapy (opcional)
    try:
        from scapy.all import ARP, Ether, srp
    except ImportError:
        print("Aviso: Scapy não encontrado. Algumas funcionalidades avançadas de varredura não estarão disponíveis.")
        print("Para instalar o Scapy, execute: pip install scapy")
except ImportError as e:
    # Exibe uma mensagem de erro e sai
    print(f"Erro ao importar bibliotecas: {e}")
    print("Verifique se todas as bibliotecas necessárias estão instaladas.")
    sys.exit(1)

def create_directories():
    """Cria os diretórios necessários para a aplicação."""
    # Diretórios para dados e recursos
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/history", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("assets/icons", exist_ok=True)
    os.makedirs("assets/images", exist_ok=True)

def main():
    """Função principal para iniciar a aplicação."""
    try:
        # Cria os diretórios necessários
        create_directories()
        
        # Cria a janela principal
        root = tk.Tk()
        
        # Configura o título e o ícone
        root.title("Mini Ferramenta de Varredura de Rede")
        
        # Cria a aplicação
        app = NetworkScannerGUI(root)
        
        # Inicia o loop principal
        root.mainloop()
        
    except Exception as e:
        # Exibe uma mensagem de erro
        print(f"Erro ao iniciar a aplicação: {e}")
        messagebox.showerror("Erro", f"Erro ao iniciar a aplicação: {e}")
        sys.exit(1)

# Ponto de entrada
if __name__ == "__main__":
    main()
