#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Interface Gráfica
--------------------------
Este módulo contém a interface gráfica Tkinter para a ferramenta de varredura de rede.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import platform
import webbrowser
from datetime import datetime
import ipaddress
import math
from PIL import Image, ImageTk, ImageDraw

# Importa os módulos da aplicação
try:
    from network_scanner import NetworkScanner
    from data_manager import DataManager
    from heatmap_utils import get_heat_color, create_heatmap_legend, get_heat_radius
    from advanced_visualization import AdvancedVisualizationManager
except ImportError:
    print("Erro ao importar módulos da aplicação. Verifique se os arquivos estão no mesmo diretório.")
    sys.exit(1)

class NetworkScannerGUI:
    """Classe principal da interface gráfica."""
    
    def __init__(self, root):
        """
        Inicializa a interface gráfica.
        
        Args:
            root: Janela principal Tkinter
        """
        self.root = root
        self.root.title("Mini Ferramenta de Varredura de Rede")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configura o ícone da aplicação (será substituído por um ícone real)
        self.create_default_icon()
        
        # Inicializa os módulos da aplicação
        self.scanner = NetworkScanner()
        self.data_manager = DataManager()
        
        # Variáveis de controle
        self.scan_running = False
        self.scan_thread = None
        self.port_scan_threads = {}
        self.selected_device = None
        
        # Configura o tema da interface
        self.setup_theme()
        
        # Cria os componentes da interface
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        # Inicializa o gerenciador de visualizações avançadas
        self.advanced_visualization = AdvancedVisualizationManager(self)
        
        # Atualiza as informações iniciais
        self.update_network_info()
        
        # Configura o manipulador de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Inicia a verificação periódica do status da varredura
        self.check_scan_status()
    
    def create_default_icon(self):
        """Cria um ícone padrão para a aplicação."""
        try:
            # Cria um diretório para os recursos se não existir
            os.makedirs("assets/icons", exist_ok=True)
            
            # Cria uma imagem simples para o ícone
            icon_size = 64
            icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            # Desenha um círculo azul com linhas representando uma rede
            draw.ellipse((4, 4, icon_size-4, icon_size-4), outline=(0, 120, 215), width=2)
            draw.line((icon_size//2, 4, icon_size//2, icon_size-4), fill=(0, 120, 215), width=2)
            draw.line((4, icon_size//2, icon_size-4, icon_size//2), fill=(0, 120, 215), width=2)
            
            # Desenha pontos representando dispositivos
            for x, y in [(16, 16), (48, 16), (16, 48), (48, 48)]:
                draw.ellipse((x-4, y-4, x+4, y+4), fill=(0, 120, 215))
            
            # Salva o ícone
            icon_path = "assets/icons/app_icon.png"
            icon.save(icon_path)
            
            # Configura o ícone da aplicação
            icon_image = ImageTk.PhotoImage(icon)
            self.root.iconphoto(True, icon_image)
            
        except Exception as e:
            print(f"Erro ao criar ícone padrão: {e}")
    
    def setup_theme(self):
        """Configura o tema da interface."""
        # Configura o estilo ttk
        self.style = ttk.Style()
        
        # Usa o tema claro padrão
        if self.style.theme_names():
            if 'vista' in self.style.theme_names():
                self.style.theme_use('vista')
            elif 'winnative' in self.style.theme_names():
                self.style.theme_use('winnative')
            elif 'clam' in self.style.theme_names():
                self.style.theme_use('clam')
        
        # Configura cores e estilos personalizados
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        self.style.configure('Status.TLabel', font=('Segoe UI', 9))
        
        # Configura cores para os dispositivos na tabela
        self.device_colors = {
            'gateway': '#FFD700',  # Dourado para o gateway
            'local': '#90EE90',    # Verde claro para o dispositivo local
            'online': '#FFFFFF',   # Branco para dispositivos online
            'unknown': '#F0F0F0'   # Cinza claro para dispositivos desconhecidos
        }
    
    def create_menu(self):
        """Cria a barra de menu da aplicação."""
        self.menu_bar = tk.Menu(self.root)
        
        # Menu Arquivo
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Nova Varredura", command=self.start_scan)
        file_menu.add_command(label="Parar Varredura", command=self.stop_scan)
        file_menu.add_separator()
        file_menu.add_command(label="Salvar Resultados", command=self.save_results)
        file_menu.add_command(label="Exportar para CSV", command=lambda: self.export_results('csv'))
        file_menu.add_command(label="Exportar para TXT", command=lambda: self.export_results('txt'))
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_close)
        self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Histórico
        history_menu = tk.Menu(self.menu_bar, tearoff=0)
        history_menu.add_command(label="Carregar Varredura Anterior", command=self.load_scan)
        history_menu.add_command(label="Gerenciar Histórico", command=self.manage_history)
        history_menu.add_separator()
        history_menu.add_command(label="Limpar Histórico", command=self.clear_history)
        self.menu_bar.add_cascade(label="Histórico", menu=history_menu)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="Configurações", command=self.show_settings)
        tools_menu.add_command(label="Visualização de Rede", command=self.show_network_visualization)
        tools_menu.add_separator()
        tools_menu.add_command(label="Visualização 3D", command=lambda: self.advanced_visualization.show_3d_visualization())
        tools_menu.add_command(label="Visualização Geoespacial", command=lambda: self.advanced_visualization.show_geospatial_visualization())
        self.menu_bar.add_cascade(label="Ferramentas", menu=tools_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Ajuda", command=self.show_help)
        help_menu.add_command(label="Sobre", command=self.show_about)
        self.menu_bar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.root.config(menu=self.menu_bar)
    
    def create_main_frame(self):
        """Cria o frame principal da aplicação."""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior para informações da rede
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Informações da Rede", padding=10)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        # Grid para informações da rede
        self.info_grid = ttk.Frame(self.info_frame)
        self.info_grid.pack(fill=tk.X)
        
        # Rótulos para informações da rede
        ttk.Label(self.info_grid, text="IP Local:", width=15, anchor=tk.E).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.local_ip_label = ttk.Label(self.info_grid, text="Carregando...")
        self.local_ip_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Gateway:", width=15, anchor=tk.E).grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.gateway_label = ttk.Label(self.info_grid, text="Carregando...")
        self.gateway_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Rede:", width=15, anchor=tk.E).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.network_label = ttk.Label(self.info_grid, text="Carregando...")
        self.network_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Status:", width=15, anchor=tk.E).grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.status_label = ttk.Label(self.info_grid, text="Pronto")
        self.status_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Frame para controles de varredura
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        # Botões de controle
        self.scan_button = ttk.Button(self.control_frame, text="Iniciar Varredura", command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Parar", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Opções de varredura
        ttk.Label(self.control_frame, text="Intervalo de Portas:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.port_start_var = tk.StringVar(value="1")
        self.port_start_entry = ttk.Entry(self.control_frame, width=6, textvariable=self.port_start_var)
        self.port_start_entry.pack(side=tk.LEFT)
        
        ttk.Label(self.control_frame, text="-").pack(side=tk.LEFT)
        
        self.port_end_var = tk.StringVar(value="1024")
        self.port_end_entry = ttk.Entry(self.control_frame, width=6, textvariable=self.port_end_var)
        self.port_end_entry.pack(side=tk.LEFT)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Frame para notebook (abas)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Aba de dispositivos
        self.devices_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.devices_frame, text="Dispositivos")
        
        # Tabela de dispositivos
        self.create_devices_table()
        
        # Aba de detalhes
        self.details_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.details_frame, text="Detalhes")
        
        # Painel de detalhes
        self.create_details_panel()
        
        # Aba de visualização
        self.visualization_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.visualization_frame, text="Visualização")
        
        # Visualização da rede
        self.create_network_visualization()
    
    def create_devices_table(self):
        """Cria a tabela de dispositivos."""
        # Frame para a tabela
        table_frame = ttk.Frame(self.devices_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Colunas da tabela
        columns = ("ip", "hostname", "mac", "status", "os", "ports")
        
        # Treeview (tabela)
        self.devices_table = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        self.devices_table.pack(fill=tk.BOTH, expand=True)
        
        # Configura a scrollbar
        scrollbar.config(command=self.devices_table.yview)
        
        # Configura as colunas
        self.devices_table.heading("ip", text="Endereço IP")
        self.devices_table.heading("hostname", text="Nome do Host")
        self.devices_table.heading("mac", text="Endereço MAC")
        self.devices_table.heading("status", text="Status")
        self.devices_table.heading("os", text="Sistema Operacional")
        self.devices_table.heading("ports", text="Portas Abertas")
        
        # Configura a largura das colunas
        self.devices_table.column("ip", width=120, anchor=tk.W)
        self.devices_table.column("hostname", width=150, anchor=tk.W)
        self.devices_table.column("mac", width=150, anchor=tk.W)
        self.devices_table.column("status", width=80, anchor=tk.CENTER)
        self.devices_table.column("os", width=120, anchor=tk.W)
        self.devices_table.column("ports", width=180, anchor=tk.W)
        
        # Configura o evento de seleção
        self.devices_table.bind("<<TreeviewSelect>>", self.on_device_select)
        
        # Menu de contexto para a tabela
        self.create_table_context_menu()
    
    def create_table_context_menu(self):
        """Cria o menu de contexto para a tabela de dispositivos."""
        self.table_context_menu = tk.Menu(self.devices_table, tearoff=0)
        self.table_context_menu.add_command(label="Verificar Portas", command=self.scan_ports_for_selected)
        self.table_context_menu.add_command(label="Copiar IP", command=lambda: self.copy_to_clipboard("ip"))
        self.table_context_menu.add_command(label="Copiar MAC", command=lambda: self.copy_to_clipboard("mac"))
        self.table_context_menu.add_command(label="Copiar Hostname", command=lambda: self.copy_to_clipboard("hostname"))
        self.table_context_menu.add_separator()
        self.table_context_menu.add_command(label="Abrir no Navegador", command=self.open_in_browser)
        
        # Vincula o botão direito do mouse ao menu de contexto
        self.devices_table.bind("<Button-3>", self.show_table_context_menu)
    
    def show_table_context_menu(self, event):
        """Exibe o menu de contexto da tabela."""
        # Seleciona o item sob o cursor
        item = self.devices_table.identify_row(event.y)
        if item:
            self.devices_table.selection_set(item)
            self.table_context_menu.post(event.x_root, event.y_root)
    
    def create_details_panel(self):
        """Cria o painel de detalhes do dispositivo selecionado."""
        # Frame para informações básicas
        basic_info_frame = ttk.LabelFrame(self.details_frame, text="Informações Básicas", padding=10)
        basic_info_frame.pack(fill=tk.X, pady=5)
        
        # Grid para informações básicas
        self.basic_grid = ttk.Frame(basic_info_frame)
        self.basic_grid.pack(fill=tk.X)
        
        # Rótulos para informações básicas
        ttk.Label(self.basic_grid, text="Endereço IP:", width=15, anchor=tk.E).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_ip_label = ttk.Label(self.basic_grid, text="-")
        self.detail_ip_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.basic_grid, text="Nome do Host:", width=15, anchor=tk.E).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_hostname_label = ttk.Label(self.basic_grid, text="-")
        self.detail_hostname_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.basic_grid, text="Endereço MAC:", width=15, anchor=tk.E).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_mac_label = ttk.Label(self.basic_grid, text="-")
        self.detail_mac_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.basic_grid, text="Status:", width=15, anchor=tk.E).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_status_label = ttk.Label(self.basic_grid, text="-")
        self.detail_status_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Adiciona o rótulo para o sistema operacional
        ttk.Label(self.basic_grid, text="Sistema Operacional:", width=15, anchor=tk.E).grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_os_label = ttk.Label(self.basic_grid, text="Desconhecido")
        self.detail_os_label.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        self.detail_os_label_title = True
        
        # Frame para portas
        ports_frame = ttk.LabelFrame(self.details_frame, text="Portas Abertas", padding=10)
        ports_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame para a tabela de portas
        ports_table_frame = ttk.Frame(ports_frame)
        ports_table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para a tabela de portas
        ports_scrollbar = ttk.Scrollbar(ports_table_frame)
        ports_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Colunas da tabela de portas
        port_columns = ("port", "service", "description")
        
        # Tabela de portas
        self.ports_table = ttk.Treeview(ports_table_frame, columns=port_columns, show="headings", yscrollcommand=ports_scrollbar.set)
        self.ports_table.pack(fill=tk.BOTH, expand=True)
        
        # Configura a scrollbar
        ports_scrollbar.config(command=self.ports_table.yview)
        
        # Configura as colunas
        self.ports_table.heading("port", text="Porta")
        self.ports_table.heading("service", text="Serviço")
        self.ports_table.heading("description", text="Descrição")
        
        # Configura a largura das colunas
        self.ports_table.column("port", width=80, anchor=tk.CENTER)
        self.ports_table.column("service", width=120, anchor=tk.W)
        self.ports_table.column("description", width=300, anchor=tk.W)
        
        # Botões de ação
        action_frame = ttk.Frame(self.details_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.scan_ports_button = ttk.Button(action_frame, text="Verificar Portas", command=self.scan_ports_for_selected)
        self.scan_ports_button.pack(side=tk.LEFT, padx=5)
        
        self.open_browser_button = ttk.Button(action_frame, text="Abrir no Navegador", command=self.open_in_browser)
        self.open_browser_button.pack(side=tk.LEFT, padx=5)
    
    def create_network_visualization(self):
        """Cria a visualização gráfica da rede."""
        # Frame para controles de visualização
        vis_control_frame = ttk.Frame(self.visualization_frame)
        vis_control_frame.pack(fill=tk.X, pady=5)
        
        # Botão para atualizar a visualização
        self.update_vis_button = ttk.Button(vis_control_frame, text="Atualizar Visualização", command=self.update_network_visualization)
        self.update_vis_button.pack(side=tk.LEFT, padx=5)
        
        # Opções de visualização
        ttk.Label(vis_control_frame, text="Tipo de Visualização:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.vis_type_var = tk.StringVar(value="radial")
        vis_type_combo = ttk.Combobox(vis_control_frame, textvariable=self.vis_type_var, state="readonly", width=15)
        vis_type_combo["values"] = ("Radial", "Hierárquica", "Força")
        vis_type_combo.pack(side=tk.LEFT, padx=5)
        vis_type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_network_visualization())
        
        # Canvas para a visualização
        self.vis_canvas_frame = ttk.Frame(self.visualization_frame, borderwidth=1, relief=tk.SUNKEN)
        self.vis_canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.vis_canvas = tk.Canvas(self.vis_canvas_frame, bg="white")
        self.vis_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mensagem inicial
        self.vis_canvas.create_text(
            self.vis_canvas.winfo_reqwidth() // 2,
            self.vis_canvas.winfo_reqheight() // 2,
            text="Execute uma varredura para visualizar a rede",
            font=("Segoe UI", 12)
        )
    
    def create_status_bar(self):
        """Cria a barra de status da aplicação."""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(2, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Rótulo para mensagens de status
        self.status_message = ttk.Label(self.status_bar, text="Pronto", style="Status.TLabel")
        self.status_message.pack(side=tk.LEFT, padx=5)
        
        # Rótulo para a data/hora
        self.status_time = ttk.Label(self.status_bar, text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), style="Status.TLabel")
        self.status_time.pack(side=tk.RIGHT, padx=5)
        
        # Atualiza a hora a cada segundo
        self.update_clock()
    
    def update_clock(self):
        """Atualiza o relógio na barra de status."""
        self.status_time.config(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.root.after(1000, self.update_clock)
    
    def update_network_info(self):
        """Atualiza as informações da rede na interface."""
        self.local_ip_label.config(text=self.scanner.local_ip)
        self.gateway_label.config(text=self.scanner.gateway or "Desconhecido")
        self.network_label.config(text=self.scanner.network)
    
    def update_status(self, message):
        """Atualiza a mensagem de status."""
        self.status_message.config(text=message)
        self.status_label.config(text=message)
    
    def start_scan(self):
        """Inicia a varredura da rede."""
        if self.scan_running:
            messagebox.showinfo("Varredura em Andamento", "Uma varredura já está em andamento.")
            return
        
        # Limpa a tabela de dispositivos
        for item in self.devices_table.get_children():
            self.devices_table.delete(item)
        
        # Limpa a tabela de portas
        for item in self.ports_table.get_children():
            self.ports_table.delete(item)
        
        # Limpa os detalhes
        self.clear_device_details()
        
        # Atualiza a interface
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_status("Iniciando varredura...")
        self.progress_var.set(0)
        
        # Inicia a varredura em uma thread separada
        self.scan_running = True
        self.scan_thread = threading.Thread(target=self.run_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def run_scan(self):
        """Executa a varredura da rede em uma thread separada."""
        try:
            # Atualiza a interface
            self.root.after(0, lambda: self.update_status("Descobrindo dispositivos na rede..."))
            
            # Executa a varredura
            if platform.system() == "Windows" and hasattr(self.scanner, 'scan_network_arp'):
                results = self.scanner.scan_network_arp(self.update_device_callback)
            else:
                results = self.scanner.scan_network_ping(self.update_device_callback)
            
            # Atualiza a interface após a conclusão
            self.root.after(0, lambda: self.update_status(f"Varredura concluída. Encontrados {len(results)} dispositivos."))
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.update_network_visualization())
            
        except Exception as e:
            # Trata erros
            error_message = f"Erro durante a varredura: {e}"
            print(error_message)
            self.root.after(0, lambda: self.update_status(error_message))
            self.root.after(0, lambda: messagebox.showerror("Erro", error_message))
        
        finally:
            # Atualiza a interface
            self.scan_running = False
            self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
    
    def update_device_callback(self, ip, device_data):
        """
        Callback para atualizar a interface com dispositivos encontrados.
        
        Args:
            ip: Endereço IP do dispositivo
            device_data: Dados do dispositivo
        """
        # Atualiza a interface na thread principal
        self.root.after(0, lambda: self.add_device_to_table(ip, device_data))
    
    def add_device_to_table(self, ip, device_data):
        """
        Adiciona um dispositivo à tabela.
        
        Args:
            ip: Endereço IP do dispositivo
            device_data: Dados do dispositivo
        """
        # Obtém os dados do dispositivo
        hostname = device_data.get('hostname', 'Desconhecido')
        mac = device_data.get('mac', 'Desconhecido')
        status = device_data.get('status', 'Desconhecido')
        ports = device_data.get('ports', {})
        os_info = device_data.get('os', {'name': 'Desconhecido', 'confidence': 0})
        os_name = os_info.get('name', 'Desconhecido')
        
        # Formata a lista de portas
        ports_str = ', '.join([f"{port}" for port in ports.keys()]) if ports else 'Nenhuma'
        
        # Verifica se o dispositivo já está na tabela
        for item in self.devices_table.get_children():
            if self.devices_table.item(item, 'values')[0] == ip:
                # Atualiza o item existente
                self.devices_table.item(item, values=(ip, hostname, mac, status, os_name, ports_str))
                return
        
        # Adiciona o dispositivo à tabela
        item_id = self.devices_table.insert('', 'end', values=(ip, hostname, mac, status, os_name, ports_str))
        
        # Define a cor de fundo com base no tipo de dispositivo
        if ip == self.scanner.gateway:
            self.devices_table.item(item_id, tags=('gateway',))
        elif ip == self.scanner.local_ip:
            self.devices_table.item(item_id, tags=('local',))
        else:
            self.devices_table.item(item_id, tags=('online',))
        
        # Configura as cores das tags
        self.devices_table.tag_configure('gateway', background=self.device_colors['gateway'])
        self.devices_table.tag_configure('local', background=self.device_colors['local'])
        self.devices_table.tag_configure('online', background=self.device_colors['online'])
    
    def stop_scan(self):
        """Interrompe a varredura em andamento."""
        if not self.scan_running:
            return
        
        # Interrompe a varredura
        self.scanner.stop_scan()
        
        # Atualiza a interface
        self.update_status("Interrompendo varredura...")
        
        # Aguarda a conclusão da thread
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(2.0)  # Aguarda até 2 segundos
        
        # Atualiza a interface
        self.scan_running = False
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("Varredura interrompida.")
    
    def on_device_select(self, event):
        """Manipula a seleção de um dispositivo na tabela."""
        # Obtém o item selecionado
        selection = self.devices_table.selection()
        if not selection:
            return
        
        # Obtém os dados do dispositivo selecionado
        item = selection[0]
        values = self.devices_table.item(item, 'values')
        
        # Extrai os valores
        ip = values[0]
        hostname = values[1]
        mac = values[2]
        status = values[3]
        
        # Armazena o dispositivo selecionado
        self.selected_device = ip
        
        # Atualiza os detalhes
        self.detail_ip_label.config(text=ip)
        self.detail_hostname_label.config(text=hostname)
        self.detail_mac_label.config(text=mac)
        self.detail_status_label.config(text=status)
        
        # Atualiza informação do sistema operacional
        if ip in self.scanner.scan_results and 'os' in self.scanner.scan_results[ip]:
            os_info = self.scanner.scan_results[ip]['os']
            os_name = os_info.get('name', 'Desconhecido')
            os_confidence = os_info.get('confidence', 0)
            
            # Atualiza o rótulo existente
            self.detail_os_label.config(text=f"{os_name} ({os_confidence:.0f}% confiança)")
        else:
            # Se não houver informação de SO, mostra "Desconhecido"
            self.detail_os_label.config(text="Desconhecido")
        
        # Limpa a tabela de portas
        for item in self.ports_table.get_children():
            self.ports_table.delete(item)
        
        # Adiciona as portas à tabela
        if ip in self.scanner.scan_results:
            ports = self.scanner.scan_results[ip].get('ports', {})
            for port, service in ports.items():
                # Descrição do serviço
                description = self.get_service_description(service)
                
                # Adiciona à tabela
                self.ports_table.insert('', 'end', values=(port, service, description))
    
    def clear_device_details(self):
        """Limpa os detalhes do dispositivo."""
        self.detail_ip_label.config(text="-")
        self.detail_hostname_label.config(text="-")
        self.detail_mac_label.config(text="-")
        self.detail_status_label.config(text="-")
        
        # Limpa a tabela de portas
        for item in self.ports_table.get_children():
            self.ports_table.delete(item)
        
        # Limpa o dispositivo selecionado
        self.selected_device = None
    
    def scan_ports_for_selected(self):
        """Verifica as portas do dispositivo selecionado."""
        if not self.selected_device:
            messagebox.showinfo("Nenhum Dispositivo Selecionado", "Selecione um dispositivo para verificar as portas.")
            return
        
        # Verifica se já existe uma varredura em andamento para este dispositivo
        if self.selected_device in self.port_scan_threads and self.port_scan_threads[self.selected_device].is_alive():
            messagebox.showinfo("Varredura em Andamento", f"Uma varredura de portas já está em andamento para {self.selected_device}.")
            return
        
        try:
            # Obtém o intervalo de portas
            start_port = int(self.port_start_var.get())
            end_port = int(self.port_end_var.get())
            
            # Valida o intervalo
            if start_port < 1 or start_port > 65535 or end_port < 1 or end_port > 65535 or start_port > end_port:
                messagebox.showerror("Intervalo Inválido", "O intervalo de portas deve estar entre 1 e 65535, e o início deve ser menor que o fim.")
                return
            
            # Atualiza a interface
            self.update_status(f"Verificando portas em {self.selected_device}...")
            
            # Limpa a tabela de portas
            for item in self.ports_table.get_children():
                self.ports_table.delete(item)
            
            # Inicia a varredura em uma thread separada
            thread = threading.Thread(
                target=self.run_port_scan,
                args=(self.selected_device, (start_port, end_port))
            )
            thread.daemon = True
            thread.start()
            
            # Armazena a thread
            self.port_scan_threads[self.selected_device] = thread
            
        except ValueError:
            messagebox.showerror("Erro", "Os valores de porta devem ser números inteiros.")
    
    def run_port_scan(self, ip, port_range):
        """
        Executa a varredura de portas em uma thread separada.
        
        Args:
            ip: Endereço IP do dispositivo
            port_range: Tupla com intervalo de portas (início, fim)
        """
        try:
            # Executa a varredura
            self.scanner.scan_ports(ip, port_range, self.update_port_callback)
            
            # Atualiza a interface após a conclusão
            self.root.after(0, lambda: self.update_status(f"Varredura de portas concluída para {ip}."))
            
            # Atualiza a tabela de dispositivos
            if ip in self.scanner.scan_results:
                device_data = self.scanner.scan_results[ip]
                self.root.after(0, lambda: self.add_device_to_table(ip, device_data))
            
        except Exception as e:
            # Trata erros
            error_message = f"Erro durante a varredura de portas: {e}"
            print(error_message)
            self.root.after(0, lambda: self.update_status(error_message))
            self.root.after(0, lambda: messagebox.showerror("Erro", error_message))
    
    def update_port_callback(self, ip, port, service):
        """
        Callback para atualizar a interface com portas encontradas.
        
        Args:
            ip: Endereço IP do dispositivo
            port: Número da porta
            service: Nome do serviço
        """
        # Atualiza a interface na thread principal
        self.root.after(0, lambda: self.add_port_to_table(ip, port, service))
    
    def add_port_to_table(self, ip, port, service):
        """
        Adiciona uma porta à tabela de portas.
        
        Args:
            ip: Endereço IP do dispositivo
            port: Número da porta
            service: Nome do serviço
        """
        # Verifica se o dispositivo selecionado ainda é o mesmo
        if self.selected_device != ip:
            return
        
        # Descrição do serviço
        description = self.get_service_description(service)
        
        # Adiciona à tabela
        self.ports_table.insert('', 'end', values=(port, service, description))
    
    def get_service_description(self, service):
        """
        Obtém a descrição de um serviço.
        
        Args:
            service: Nome do serviço
            
        Returns:
            str: Descrição do serviço
        """
        # Descrições comuns de serviços
        descriptions = {
            'http': 'Servidor Web (HTTP)',
            'https': 'Servidor Web Seguro (HTTPS)',
            'ftp': 'Servidor de Transferência de Arquivos (FTP)',
            'ssh': 'Acesso Remoto Seguro (SSH)',
            'telnet': 'Acesso Remoto (Telnet)',
            'smtp': 'Servidor de E-mail (SMTP)',
            'pop3': 'Recebimento de E-mail (POP3)',
            'imap': 'Acesso a E-mail (IMAP)',
            'dns': 'Servidor de Nomes (DNS)',
            'dhcp': 'Configuração Automática de Rede (DHCP)',
            'rdp': 'Área de Trabalho Remota (RDP)',
            'vnc': 'Controle Remoto (VNC)',
            'mysql': 'Banco de Dados MySQL',
            'mssql': 'Banco de Dados Microsoft SQL Server',
            'smb': 'Compartilhamento de Arquivos Windows (SMB)',
            'netbios': 'Serviço de Rede Windows (NetBIOS)',
            'snmp': 'Gerenciamento de Rede (SNMP)',
            'ldap': 'Diretório de Rede (LDAP)',
            'ntp': 'Sincronização de Tempo (NTP)',
            'irc': 'Chat (IRC)',
            'pptp': 'VPN Point-to-Point (PPTP)',
            'l2tp': 'VPN Layer 2 (L2TP)',
            'openvpn': 'VPN OpenVPN',
            'ipsec': 'VPN IPsec',
            'sip': 'Telefonia IP (SIP)',
            'rtsp': 'Streaming de Mídia (RTSP)',
            'http-proxy': 'Proxy HTTP',
            'socks': 'Proxy SOCKS',
            'unknown': 'Serviço Desconhecido'
        }
        
        return descriptions.get(service.lower(), 'Serviço não identificado')
    
    def copy_to_clipboard(self, field):
        """
        Copia um valor para a área de transferência.
        
        Args:
            field: Campo a ser copiado (ip, mac, hostname)
        """
        if not self.selected_device:
            return
        
        # Obtém o valor
        if field == "ip":
            value = self.detail_ip_label.cget("text")
        elif field == "mac":
            value = self.detail_mac_label.cget("text")
        elif field == "hostname":
            value = self.detail_hostname_label.cget("text")
        else:
            return
        
        # Copia para a área de transferência
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        
        # Atualiza o status
        self.update_status(f"{field.upper()} copiado para a área de transferência: {value}")
    
    def open_in_browser(self):
        """Abre o dispositivo selecionado no navegador."""
        if not self.selected_device:
            messagebox.showinfo("Nenhum Dispositivo Selecionado", "Selecione um dispositivo para abrir no navegador.")
            return
        
        # Verifica se o dispositivo tem a porta 80 (HTTP) ou 443 (HTTPS) aberta
        ip = self.selected_device
        if ip in self.scanner.scan_results:
            ports = self.scanner.scan_results[ip].get('ports', {})
            
            # Determina o protocolo
            if 443 in ports:
                url = f"https://{ip}"
            elif 80 in ports:
                url = f"http://{ip}"
            else:
                # Pergunta ao usuário qual protocolo usar
                if messagebox.askyesno("Protocolo", "Não foi detectado servidor web (portas 80/443). Tentar abrir como HTTP?"):
                    url = f"http://{ip}"
                else:
                    return
            
            # Abre o navegador
            try:
                webbrowser.open(url)
                self.update_status(f"Abrindo {url} no navegador...")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir o navegador: {e}")
    
    def save_results(self):
        """Salva os resultados da varredura."""
        # Verifica se há resultados para salvar
        if not self.scanner.scan_results:
            messagebox.showinfo("Sem Resultados", "Não há resultados de varredura para salvar.")
            return
        
        try:
            # Obtém os dados da varredura
            scan_data = self.scanner.get_scan_summary()
            
            # Salva os resultados
            filepath = self.data_manager.save_scan_results(scan_data)
            
            # Atualiza o status
            self.update_status(f"Resultados salvos em {filepath}")
            
            # Exibe mensagem de confirmação
            messagebox.showinfo("Resultados Salvos", f"Os resultados da varredura foram salvos com sucesso em:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar os resultados: {e}")
    
    def export_results(self, format_type):
        """
        Exporta os resultados da varredura para um arquivo.
        
        Args:
            format_type: Tipo de formato (csv, txt)
        """
        # Verifica se há resultados para exportar
        if not self.scanner.scan_results:
            messagebox.showinfo("Sem Resultados", "Não há resultados de varredura para exportar.")
            return
        
        try:
            # Obtém os dados da varredura
            scan_data = self.scanner.get_scan_summary()
            
            # Solicita o local para salvar o arquivo
            if format_type.lower() == 'csv':
                filetypes = [("Arquivos CSV", "*.csv"), ("Todos os Arquivos", "*.*")]
                default_ext = ".csv"
                title = "Exportar para CSV"
            else:  # txt
                filetypes = [("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
                default_ext = ".txt"
                title = "Exportar para TXT"
            
            filepath = filedialog.asksaveasfilename(
                title=title,
                filetypes=filetypes,
                defaultextension=default_ext
            )
            
            if not filepath:
                return  # Usuário cancelou
            
            # Exporta os resultados
            if format_type.lower() == 'csv':
                success = self.data_manager.export_to_csv(scan_data, filepath)
            else:  # txt
                success = self.data_manager.export_to_txt(scan_data, filepath)
            
            if success:
                # Atualiza o status
                self.update_status(f"Resultados exportados para {filepath}")
                
                # Exibe mensagem de confirmação
                messagebox.showinfo("Exportação Concluída", f"Os resultados da varredura foram exportados com sucesso para:\n{filepath}")
            else:
                messagebox.showerror("Erro", "Erro ao exportar os resultados.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar os resultados: {e}")
    
    def load_scan(self):
        """Carrega resultados de uma varredura anterior."""
        try:
            # Obtém a lista de varreduras
            history = self.data_manager.get_scan_history()
            
            if not history:
                messagebox.showinfo("Sem Histórico", "Não há varreduras anteriores para carregar.")
                return
            
            # Cria uma janela para selecionar a varredura
            select_window = tk.Toplevel(self.root)
            select_window.title("Carregar Varredura Anterior")
            select_window.geometry("600x400")
            select_window.minsize(600, 400)
            select_window.transient(self.root)
            select_window.grab_set()
            
            # Frame para a lista
            list_frame = ttk.Frame(select_window, padding=10)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Colunas da lista
            columns = ("timestamp", "network", "devices", "ports")
            
            # Lista de varreduras
            history_list = ttk.Treeview(list_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
            history_list.pack(fill=tk.BOTH, expand=True)
            
            # Configura a scrollbar
            scrollbar.config(command=history_list.yview)
            
            # Configura as colunas
            history_list.heading("timestamp", text="Data/Hora")
            history_list.heading("network", text="Rede")
            history_list.heading("devices", text="Dispositivos")
            history_list.heading("ports", text="Portas Abertas")
            
            # Configura a largura das colunas
            history_list.column("timestamp", width=150, anchor=tk.W)
            history_list.column("network", width=120, anchor=tk.W)
            history_list.column("devices", width=100, anchor=tk.CENTER)
            history_list.column("ports", width=100, anchor=tk.CENTER)
            
            # Adiciona os itens à lista
            for item in history:
                history_list.insert('', 'end', values=(
                    item['timestamp'],
                    item['network'],
                    item['total_devices'],
                    item['total_open_ports']
                ), tags=(item['filename'],))
            
            # Frame para botões
            button_frame = ttk.Frame(select_window, padding=10)
            button_frame.pack(fill=tk.X)
            
            # Botão para carregar
            load_button = ttk.Button(button_frame, text="Carregar", command=lambda: self.do_load_scan(history_list, select_window))
            load_button.pack(side=tk.RIGHT, padx=5)
            
            # Botão para cancelar
            cancel_button = ttk.Button(button_frame, text="Cancelar", command=select_window.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o histórico de varreduras: {e}")
    
    def do_load_scan(self, history_list, window):
        """
        Carrega a varredura selecionada.
        
        Args:
            history_list: Lista de varreduras
            window: Janela de seleção
        """
        # Obtém o item selecionado
        selection = history_list.selection()
        if not selection:
            messagebox.showinfo("Nenhuma Varredura Selecionada", "Selecione uma varredura para carregar.")
            return
        
        # Obtém o nome do arquivo
        item = selection[0]
        filename = history_list.item(item, 'tags')[0]
        
        # Fecha a janela
        window.destroy()
        
        try:
            # Carrega os dados
            scan_data = self.data_manager.load_scan_results(filename)
            
            if not scan_data:
                messagebox.showerror("Erro", "Erro ao carregar os dados da varredura.")
                return
            
            # Limpa a tabela de dispositivos
            for item in self.devices_table.get_children():
                self.devices_table.delete(item)
            
            # Limpa a tabela de portas
            for item in self.ports_table.get_children():
                self.ports_table.delete(item)
            
            # Limpa os detalhes
            self.clear_device_details()
            
            # Atualiza as informações da rede
            self.scanner.local_ip = scan_data.get('local_ip', self.scanner.local_ip)
            self.scanner.gateway = scan_data.get('gateway', self.scanner.gateway)
            self.scanner.network = scan_data.get('network', self.scanner.network)
            self.update_network_info()
            
            # Atualiza os resultados da varredura
            self.scanner.scan_results = scan_data.get('devices', {})
            
            # Adiciona os dispositivos à tabela
            for ip, device_data in self.scanner.scan_results.items():
                self.add_device_to_table(ip, device_data)
            
            # Atualiza a visualização da rede
            self.update_network_visualization()
            
            # Atualiza o status
            self.update_status(f"Varredura carregada: {scan_data.get('timestamp', 'Desconhecido')}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar a varredura: {e}")
    
    def manage_history(self):
        """Gerencia o histórico de varreduras."""
        try:
            # Obtém a lista de varreduras
            history = self.data_manager.get_scan_history()
            
            if not history:
                messagebox.showinfo("Sem Histórico", "Não há varreduras anteriores para gerenciar.")
                return
            
            # Cria uma janela para gerenciar o histórico
            manage_window = tk.Toplevel(self.root)
            manage_window.title("Gerenciar Histórico de Varreduras")
            manage_window.geometry("700x500")
            manage_window.minsize(700, 500)
            manage_window.transient(self.root)
            manage_window.grab_set()
            
            # Frame para a lista
            list_frame = ttk.Frame(manage_window, padding=10)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Colunas da lista
            columns = ("timestamp", "network", "devices", "ports", "filename")
            
            # Lista de varreduras
            history_list = ttk.Treeview(list_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
            history_list.pack(fill=tk.BOTH, expand=True)
            
            # Configura a scrollbar
            scrollbar.config(command=history_list.yview)
            
            # Configura as colunas
            history_list.heading("timestamp", text="Data/Hora")
            history_list.heading("network", text="Rede")
            history_list.heading("devices", text="Dispositivos")
            history_list.heading("ports", text="Portas Abertas")
            history_list.heading("filename", text="Arquivo")
            
            # Configura a largura das colunas
            history_list.column("timestamp", width=150, anchor=tk.W)
            history_list.column("network", width=120, anchor=tk.W)
            history_list.column("devices", width=100, anchor=tk.CENTER)
            history_list.column("ports", width=100, anchor=tk.CENTER)
            history_list.column("filename", width=200, anchor=tk.W)
            
            # Adiciona os itens à lista
            for item in history:
                history_list.insert('', 'end', values=(
                    item['timestamp'],
                    item['network'],
                    item['total_devices'],
                    item['total_open_ports'],
                    item['filename']
                ))
            
            # Frame para botões
            button_frame = ttk.Frame(manage_window, padding=10)
            button_frame.pack(fill=tk.X)
            
            # Botão para carregar
            load_button = ttk.Button(button_frame, text="Carregar", command=lambda: self.do_load_scan_from_manage(history_list, manage_window))
            load_button.pack(side=tk.LEFT, padx=5)
            
            # Botão para excluir
            delete_button = ttk.Button(button_frame, text="Excluir", command=lambda: self.delete_scan(history_list))
            delete_button.pack(side=tk.LEFT, padx=5)
            
            # Botão para exportar
            export_button = ttk.Button(button_frame, text="Exportar", command=lambda: self.export_scan_from_manage(history_list))
            export_button.pack(side=tk.LEFT, padx=5)
            
            # Botão para fechar
            close_button = ttk.Button(button_frame, text="Fechar", command=manage_window.destroy)
            close_button.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerenciar o histórico de varreduras: {e}")
    
    def do_load_scan_from_manage(self, history_list, window):
        """
        Carrega a varredura selecionada a partir da janela de gerenciamento.
        
        Args:
            history_list: Lista de varreduras
            window: Janela de gerenciamento
        """
        # Obtém o item selecionado
        selection = history_list.selection()
        if not selection:
            messagebox.showinfo("Nenhuma Varredura Selecionada", "Selecione uma varredura para carregar.")
            return
        
        # Obtém o nome do arquivo
        item = selection[0]
        values = history_list.item(item, 'values')
        filename = values[4]
        
        # Fecha a janela
        window.destroy()
        
        try:
            # Carrega os dados
            scan_data = self.data_manager.load_scan_results(filename)
            
            if not scan_data:
                messagebox.showerror("Erro", "Erro ao carregar os dados da varredura.")
                return
            
            # Limpa a tabela de dispositivos
            for item in self.devices_table.get_children():
                self.devices_table.delete(item)
            
            # Limpa a tabela de portas
            for item in self.ports_table.get_children():
                self.ports_table.delete(item)
            
            # Limpa os detalhes
            self.clear_device_details()
            
            # Atualiza as informações da rede
            self.scanner.local_ip = scan_data.get('local_ip', self.scanner.local_ip)
            self.scanner.gateway = scan_data.get('gateway', self.scanner.gateway)
            self.scanner.network = scan_data.get('network', self.scanner.network)
            self.update_network_info()
            
            # Atualiza os resultados da varredura
            self.scanner.scan_results = scan_data.get('devices', {})
            
            # Adiciona os dispositivos à tabela
            for ip, device_data in self.scanner.scan_results.items():
                self.add_device_to_table(ip, device_data)
            
            # Atualiza a visualização da rede
            self.update_network_visualization()
            
            # Atualiza o status
            self.update_status(f"Varredura carregada: {scan_data.get('timestamp', 'Desconhecido')}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar a varredura: {e}")
    
    def delete_scan(self, history_list):
        """
        Exclui a varredura selecionada.
        
        Args:
            history_list: Lista de varreduras
        """
        # Obtém o item selecionado
        selection = history_list.selection()
        if not selection:
            messagebox.showinfo("Nenhuma Varredura Selecionada", "Selecione uma varredura para excluir.")
            return
        
        # Obtém o nome do arquivo
        item = selection[0]
        values = history_list.item(item, 'values')
        filename = values[4]
        
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a varredura de {values[0]}?"):
            return
        
        try:
            # Exclui o arquivo
            success = self.data_manager.delete_scan_result(filename)
            
            if success:
                # Remove o item da lista
                history_list.delete(item)
                
                # Atualiza o status
                self.update_status(f"Varredura excluída: {filename}")
            else:
                messagebox.showerror("Erro", "Erro ao excluir a varredura.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir a varredura: {e}")
    
    def export_scan_from_manage(self, history_list):
        """
        Exporta a varredura selecionada.
        
        Args:
            history_list: Lista de varreduras
        """
        # Obtém o item selecionado
        selection = history_list.selection()
        if not selection:
            messagebox.showinfo("Nenhuma Varredura Selecionada", "Selecione uma varredura para exportar.")
            return
        
        # Obtém o nome do arquivo
        item = selection[0]
        values = history_list.item(item, 'values')
        filename = values[4]
        
        try:
            # Carrega os dados
            scan_data = self.data_manager.load_scan_results(filename)
            
            if not scan_data:
                messagebox.showerror("Erro", "Erro ao carregar os dados da varredura.")
                return
            
            # Pergunta o formato de exportação
            format_type = messagebox.askquestion("Formato de Exportação", "Exportar como CSV?")
            
            if format_type == 'yes':
                format_type = 'csv'
                filetypes = [("Arquivos CSV", "*.csv"), ("Todos os Arquivos", "*.*")]
                default_ext = ".csv"
                title = "Exportar para CSV"
            else:
                format_type = 'txt'
                filetypes = [("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
                default_ext = ".txt"
                title = "Exportar para TXT"
            
            # Solicita o local para salvar o arquivo
            filepath = filedialog.asksaveasfilename(
                title=title,
                filetypes=filetypes,
                defaultextension=default_ext
            )
            
            if not filepath:
                return  # Usuário cancelou
            
            # Exporta os resultados
            if format_type == 'csv':
                success = self.data_manager.export_to_csv(scan_data, filepath)
            else:  # txt
                success = self.data_manager.export_to_txt(scan_data, filepath)
            
            if success:
                # Atualiza o status
                self.update_status(f"Resultados exportados para {filepath}")
                
                # Exibe mensagem de confirmação
                messagebox.showinfo("Exportação Concluída", f"Os resultados da varredura foram exportados com sucesso para:\n{filepath}")
            else:
                messagebox.showerror("Erro", "Erro ao exportar os resultados.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar os resultados: {e}")
    
    def clear_history(self):
        """Limpa todo o histórico de varreduras."""
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir todo o histórico de varreduras?"):
            return
        
        try:
            # Limpa o histórico
            success = self.data_manager.clear_history()
            
            if success:
                # Atualiza o status
                self.update_status("Histórico de varreduras limpo.")
                
                # Exibe mensagem de confirmação
                messagebox.showinfo("Histórico Limpo", "O histórico de varreduras foi limpo com sucesso.")
            else:
                messagebox.showinfo("Sem Histórico", "Não há histórico para limpar.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar o histórico: {e}")
    
    def update_network_visualization(self):
        """Atualiza a visualização gráfica da rede."""
        # Limpa o canvas
        self.vis_canvas.delete("all")
        
        # Verifica se há resultados para visualizar
        if not self.scanner.scan_results:
            self.vis_canvas.create_text(
                self.vis_canvas.winfo_width() // 2,
                self.vis_canvas.winfo_height() // 2,
                text="Execute uma varredura para visualizar a rede",
                font=("Segoe UI", 12)
            )
            return
        
        # Obtém o tipo de visualização
        vis_type = self.vis_type_var.get().lower()
        
        # Desenha a visualização
        if vis_type == "radial":
            self.draw_radial_visualization()
        elif vis_type == "hierárquica":
            self.draw_hierarchical_visualization()
        else:  # força
            self.draw_force_visualization()
    
    def draw_radial_visualization(self):
        """Desenha a visualização radial da rede."""
        # Obtém as dimensões do canvas
        width = self.vis_canvas.winfo_width()
        height = self.vis_canvas.winfo_height()
        
        # Calcula o centro
        center_x = width // 2
        center_y = height // 2
        
        # Raio do círculo central (gateway)
        gateway_radius = 30
        
        # Raio do círculo de dispositivos
        device_radius = min(width, height) // 3
        
        # Tamanho dos nós
        node_radius = 15
        
        # Cores
        gateway_color = "#FFD700"  # Dourado
        local_color = "#90EE90"    # Verde claro
        device_color = "#6495ED"   # Azul
        line_color = "#CCCCCC"     # Cinza claro
        
        # Encontra o número máximo de portas abertas para escala do mapa de calor
        max_ports = 1  # Evita divisão por zero
        for ip, device_data in self.scanner.scan_results.items():
            num_ports = len(device_data.get('ports', {}))
            if num_ports > max_ports:
                max_ports = num_ports
        
        # Desenha o gateway no centro
        gateway_ip = self.scanner.gateway
        if gateway_ip and gateway_ip in self.scanner.scan_results:
            # Conta portas abertas no gateway
            gateway_ports = len(self.scanner.scan_results[gateway_ip].get('ports', {}))
            
            # Determina o raio baseado no número de portas (mapa de calor)
            heat_radius = get_heat_radius(gateway_ports, 0, max_ports, gateway_radius, gateway_radius * 1.5)
            
            # Desenha o círculo do gateway com mapa de calor
            heat_color = get_heat_color(gateway_ports, 0, max_ports)
            
            # Desenha o círculo do gateway
            self.vis_canvas.create_oval(
                center_x - heat_radius,
                center_y - heat_radius,
                center_x + heat_radius,
                center_y + heat_radius,
                fill=heat_color,
                outline="#000000",
                width=2,
                tags=("gateway", gateway_ip)
            )
            
            # Desenha o texto do gateway
            self.vis_canvas.create_text(
                center_x,
                center_y,
                text="Gateway",
                font=("Segoe UI", 10, "bold"),
                tags=("gateway_text", gateway_ip)
            )
            
            # Adiciona texto com número de portas
            if gateway_ports > 0:
                self.vis_canvas.create_text(
                    center_x,
                    center_y + 15,
                    text=f"{gateway_ports} portas",
                    font=("Segoe UI", 8),
                    tags=("gateway_ports", gateway_ip)
                )
        
        # Conta os dispositivos (excluindo o gateway)
        devices = [ip for ip in self.scanner.scan_results.keys() if ip != gateway_ip]
        num_devices = len(devices)
        
        if num_devices > 0:
            # Ângulo entre dispositivos
            angle_step = 360 / num_devices
            
            # Desenha os dispositivos em círculo
            for i, ip in enumerate(devices):
                # Calcula a posição
                angle = math.radians(i * angle_step)
                x = center_x + device_radius * math.cos(angle)
                y = center_y + device_radius * math.sin(angle)
                
                # Conta portas abertas para o mapa de calor
                num_ports = len(self.scanner.scan_results[ip].get('ports', {}))
                
                # Determina o raio baseado no número de portas (mapa de calor)
                heat_radius = get_heat_radius(num_ports, 0, max_ports, node_radius, node_radius * 1.8)
                
                # Determina a cor base
                if ip == self.scanner.local_ip:
                    base_color = local_color
                    label = "Este PC"
                else:
                    # Usa o mapa de calor para a cor
                    base_color = get_heat_color(num_ports, 0, max_ports)
                    hostname = self.scanner.scan_results[ip].get('hostname')
                    if hostname:
                        label = hostname.split('.')[0]  # Usa apenas a primeira parte do hostname
                    else:
                        label = ip.split('.')[-1]  # Usa apenas o último octeto do IP
                
                # Desenha a linha para o gateway
                if gateway_ip and gateway_ip in self.scanner.scan_results:
                    self.vis_canvas.create_line(
                        center_x, center_y,
                        x, y,
                        fill=line_color,
                        width=1,
                        tags=("line", f"{gateway_ip}_{ip}")
                    )
                
                # Desenha o círculo do dispositivo com mapa de calor
                self.vis_canvas.create_oval(
                    x - heat_radius,
                    y - heat_radius,
                    x + heat_radius,
                    y + heat_radius,
                    fill=base_color,
                    outline="#000000",
                    width=1,
                    tags=("device", ip)
                )
                
                # Desenha o texto do dispositivo
                self.vis_canvas.create_text(
                    x,
                    y,
                    text=label,
                    font=("Segoe UI", 8),
                    tags=("device_text", ip)
                )
                
                # Desenha o IP abaixo do dispositivo
                self.vis_canvas.create_text(
                    x,
                    y + heat_radius + 10,
                    text=ip,
                    font=("Segoe UI", 7),
                    tags=("ip_text", ip)
                )
                
                # Adiciona texto com número de portas
                if num_ports > 0:
                    self.vis_canvas.create_text(
                        x,
                        y + 12,
                        text=f"{num_ports}",
                        font=("Segoe UI", 7, "bold"),
                        tags=("port_count", ip)
                    )
        
        # Adiciona título
        self.vis_canvas.create_text(
            center_x,
            20,
            text=f"Visualização da Rede: {self.scanner.network}",
            font=("Segoe UI", 12, "bold"),
            tags=("title")
        )
        
        # Adiciona legenda
        legend_y = height - 60
        
        # Gateway
        self.vis_canvas.create_oval(
            30, legend_y,
            50, legend_y + 20,
            fill=gateway_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            100,
            legend_y + 10,
            text="Gateway",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
        
        # Dispositivo local
        self.vis_canvas.create_oval(
            200, legend_y,
            220, legend_y + 20,
            fill=local_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            270,
            legend_y + 10,
            text="Este PC",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
        
        # Adiciona legenda do mapa de calor
        create_heatmap_legend(
            self.vis_canvas,
            width - 300,
            height - 100,
            280,
            80,
            "Mapa de Calor (portas abertas)"
        )
    
    def draw_hierarchical_visualization(self):
        """Desenha a visualização hierárquica da rede."""
        # Obtém as dimensões do canvas
        width = self.vis_canvas.winfo_width()
        height = self.vis_canvas.winfo_height()
        
        # Margens
        margin_top = 80
        margin_bottom = 60
        margin_left = 50
        margin_right = 50
        
        # Área útil
        usable_width = width - margin_left - margin_right
        usable_height = height - margin_top - margin_bottom
        
        # Tamanho dos nós
        node_radius = 15
        
        # Cores
        gateway_color = "#FFD700"  # Dourado
        local_color = "#90EE90"    # Verde claro
        device_color = "#6495ED"   # Azul
        line_color = "#CCCCCC"     # Cinza claro
        
        # Encontra o número máximo de portas abertas para escala do mapa de calor
        max_ports = 1  # Evita divisão por zero
        for ip, device_data in self.scanner.scan_results.items():
            num_ports = len(device_data.get('ports', {}))
            if num_ports > max_ports:
                max_ports = num_ports
        
        # Posição do gateway
        gateway_ip = self.scanner.gateway
        gateway_x = width // 2
        gateway_y = margin_top + 30
        
        # Desenha o gateway
        if gateway_ip and gateway_ip in self.scanner.scan_results:
            # Conta portas abertas no gateway
            gateway_ports = len(self.scanner.scan_results[gateway_ip].get('ports', {}))
            
            # Determina o raio baseado no número de portas (mapa de calor)
            heat_radius = get_heat_radius(gateway_ports, 0, max_ports, node_radius, node_radius * 1.5)
            
            # Desenha o círculo do gateway com mapa de calor
            heat_color = get_heat_color(gateway_ports, 0, max_ports)
            
            # Desenha o círculo do gateway
            self.vis_canvas.create_oval(
                gateway_x - heat_radius,
                gateway_y - heat_radius,
                gateway_x + heat_radius,
                gateway_y + heat_radius,
                fill=heat_color,
                outline="#000000",
                width=2,
                tags=("gateway", gateway_ip)
            )
            
            # Desenha o texto do gateway
            self.vis_canvas.create_text(
                gateway_x,
                gateway_y,
                text="GW",
                font=("Segoe UI", 8, "bold"),
                tags=("gateway_text", gateway_ip)
            )
            
            # Desenha o IP do gateway
            self.vis_canvas.create_text(
                gateway_x,
                gateway_y - heat_radius - 10,
                text=gateway_ip,
                font=("Segoe UI", 8),
                tags=("ip_text", gateway_ip)
            )
            
            # Adiciona texto com número de portas
            if gateway_ports > 0:
                self.vis_canvas.create_text(
                    gateway_x,
                    gateway_y + 12,
                    text=f"{gateway_ports}",
                    font=("Segoe UI", 7, "bold"),
                    tags=("port_count", gateway_ip)
                )
        
        # Conta os dispositivos (excluindo o gateway)
        devices = [ip for ip in self.scanner.scan_results.keys() if ip != gateway_ip]
        num_devices = len(devices)
        
        if num_devices > 0:
            # Calcula o espaçamento entre dispositivos
            device_spacing = usable_width / (num_devices + 1)
            
            # Posição Y dos dispositivos
            device_y = gateway_y + 100
            
            # Desenha os dispositivos em linha
            for i, ip in enumerate(devices):
                # Calcula a posição X
                device_x = margin_left + device_spacing * (i + 1)
                
                # Conta portas abertas para o mapa de calor
                num_ports = len(self.scanner.scan_results[ip].get('ports', {}))
                
                # Determina o raio baseado no número de portas (mapa de calor)
                heat_radius = get_heat_radius(num_ports, 0, max_ports, node_radius, node_radius * 1.8)
                
                # Determina a cor
                if ip == self.scanner.local_ip:
                    color = local_color
                    label = "Este PC"
                else:
                    # Usa o mapa de calor para a cor
                    color = get_heat_color(num_ports, 0, max_ports)
                    hostname = self.scanner.scan_results[ip].get('hostname')
                    if hostname:
                        label = hostname.split('.')[0]  # Usa apenas a primeira parte do hostname
                    else:
                        label = ip.split('.')[-1]  # Usa apenas o último octeto do IP
                
                # Desenha a linha para o gateway
                if gateway_ip and gateway_ip in self.scanner.scan_results:
                    self.vis_canvas.create_line(
                        gateway_x, gateway_y + heat_radius,
                        device_x, device_y - heat_radius,
                        fill=line_color,
                        width=1,
                        tags=("line", f"{gateway_ip}_{ip}")
                    )
                
                # Desenha o círculo do dispositivo com mapa de calor
                self.vis_canvas.create_oval(
                    device_x - heat_radius,
                    device_y - heat_radius,
                    device_x + heat_radius,
                    device_y + heat_radius,
                    fill=color,
                    outline="#000000",
                    width=1,
                    tags=("device", ip)
                )
                
                # Desenha o texto do dispositivo
                self.vis_canvas.create_text(
                    device_x,
                    device_y,
                    text=label,
                    font=("Segoe UI", 8),
                    tags=("device_text", ip)
                )
                
                # Desenha o IP abaixo do dispositivo
                self.vis_canvas.create_text(
                    device_x,
                    device_y + heat_radius + 10,
                    text=ip,
                    font=("Segoe UI", 7),
                    tags=("ip_text", ip)
                )
                
                # Adiciona texto com número de portas
                if num_ports > 0:
                    self.vis_canvas.create_text(
                        device_x,
                        device_y + 12,
                        text=f"{num_ports}",
                        font=("Segoe UI", 7, "bold"),
                        tags=("port_count", ip)
                    )
                
                # Linha as portas abertas, se houver
                ports = self.scanner.scan_results[ip].get('ports', {})
                if ports:
                    ports_str = ", ".join([str(port) for port in list(ports.keys())[:5]])
                    if len(ports) > 5:
                        ports_str += "..."
                    
                    self.vis_canvas.create_text(
                        device_x,
                        device_y + heat_radius + 25,
                        text=f"Portas: {ports_str}",
                        font=("Segoe UI", 7),
                        tags=("ports_text", ip)
                    )
        
        # Adiciona título
        self.vis_canvas.create_text(
            width // 2,
            20,
            text=f"Visualização Hierárquica da Rede: {self.scanner.network}",
            font=("Segoe UI", 12, "bold"),
            tags=("title")
        )
        
        # Adiciona legenda
        legend_y = height - 30
        
        # Gateway
        self.vis_canvas.create_oval(
            30, legend_y,
            50, legend_y + 20,
            fill=gateway_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            100,
            legend_y + 10,
            text="Gateway",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
        
        # Dispositivo local
        self.vis_canvas.create_oval(
            200, legend_y,
            220, legend_y + 20,
            fill=local_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            270,
            legend_y + 10,
            text="Este PC",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
        
        # Outros dispositivos
        self.vis_canvas.create_oval(
            370, legend_y,
            390, legend_y + 20,
            fill=device_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            440,
            legend_y + 10,
            text="Outros Dispositivos",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
    
    def draw_force_visualization(self):
        """Desenha a visualização de força da rede."""
        # Esta visualização é uma simulação simplificada de um layout de força
        # Em uma implementação real, seria usado um algoritmo de layout de força completo
        
        # Obtém as dimensões do canvas
        width = self.vis_canvas.winfo_width()
        height = self.vis_canvas.winfo_height()
        
        # Margens
        margin = 50
        
        # Área útil
        usable_width = width - 2 * margin
        usable_height = height - 2 * margin
        
        # Tamanho dos nós
        node_radius = 15
        
        # Cores
        gateway_color = "#FFD700"  # Dourado
        local_color = "#90EE90"    # Verde claro
        device_color = "#6495ED"   # Azul
        line_color = "#CCCCCC"     # Cinza claro
        
        # Posições dos dispositivos (simuladas)
        positions = {}
        
        # Posição do gateway
        gateway_ip = self.scanner.gateway
        if gateway_ip and gateway_ip in self.scanner.scan_results:
            positions[gateway_ip] = (width // 2, height // 2)
        
        # Gera posições aleatórias para os dispositivos
        import random
        random.seed(42)  # Para reprodutibilidade
        
        for ip in self.scanner.scan_results:
            if ip != gateway_ip:
                # Gera uma posição aleatória dentro da área útil
                x = margin + random.random() * usable_width
                y = margin + random.random() * usable_height
                positions[ip] = (x, y)
        
        # Desenha as linhas entre dispositivos
        for ip, (x, y) in positions.items():
            # Desenha a linha para o gateway
            if gateway_ip and gateway_ip in positions and ip != gateway_ip:
                gw_x, gw_y = positions[gateway_ip]
                self.vis_canvas.create_line(
                    gw_x, gw_y,
                    x, y,
                    fill=line_color,
                    width=1,
                    tags=("line", f"{gateway_ip}_{ip}")
                )
        
        # Desenha os dispositivos
        for ip, (x, y) in positions.items():
            # Determina a cor e o rótulo
            if ip == gateway_ip:
                color = gateway_color
                label = "GW"
            elif ip == self.scanner.local_ip:
                color = local_color
                label = "Este PC"
            else:
                color = device_color
                hostname = self.scanner.scan_results[ip].get('hostname')
                if hostname:
                    label = hostname.split('.')[0]  # Usa apenas a primeira parte do hostname
                else:
                    label = ip.split('.')[-1]  # Usa apenas o último octeto do IP
            
            # Desenha o círculo do dispositivo
            self.vis_canvas.create_oval(
                x - node_radius,
                y - node_radius,
                x + node_radius,
                y + node_radius,
                fill=color,
                outline="#000000",
                width=1,
                tags=("device", ip)
            )
            
            # Desenha o texto do dispositivo
            self.vis_canvas.create_text(
                x,
                y,
                text=label,
                font=("Segoe UI", 8),
                tags=("device_text", ip)
            )
            
            # Desenha o IP abaixo do dispositivo
            self.vis_canvas.create_text(
                x,
                y + node_radius + 10,
                text=ip,
                font=("Segoe UI", 7),
                tags=("ip_text", ip)
            )
        
        # Adiciona título
        self.vis_canvas.create_text(
            width // 2,
            20,
            text=f"Visualização de Força da Rede: {self.scanner.network}",
            font=("Segoe UI", 12, "bold"),
            tags=("title")
        )
        
        # Adiciona legenda
        legend_y = height - 30
        
        # Gateway
        self.vis_canvas.create_oval(
            30, legend_y,
            50, legend_y + 20,
            fill=gateway_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            100,
            legend_y + 10,
            text="Gateway",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
        
        # Dispositivo local
        self.vis_canvas.create_oval(
            200, legend_y,
            220, legend_y + 20,
            fill=local_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            270,
            legend_y + 10,
            text="Este PC",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
        
        # Outros dispositivos
        self.vis_canvas.create_oval(
            370, legend_y,
            390, legend_y + 20,
            fill=device_color,
            outline="#000000",
            width=1,
            tags=("legend")
        )
        self.vis_canvas.create_text(
            440,
            legend_y + 10,
            text="Outros Dispositivos",
            anchor=tk.W,
            font=("Segoe UI", 9),
            tags=("legend")
        )
    
    def show_settings(self):
        """Exibe a janela de configurações."""
        # Cria uma janela para as configurações
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("400x300")
        settings_window.minsize(400, 300)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Frame para as configurações
        settings_frame = ttk.Frame(settings_window, padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurações de varredura
        scan_frame = ttk.LabelFrame(settings_frame, text="Configurações de Varredura", padding=10)
        scan_frame.pack(fill=tk.X, pady=5)
        
        # Intervalo de portas padrão
        ttk.Label(scan_frame, text="Intervalo de Portas Padrão:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        port_frame = ttk.Frame(scan_frame)
        port_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Usa as variáveis existentes
        ttk.Entry(port_frame, width=6, textvariable=self.port_start_var).pack(side=tk.LEFT)
        ttk.Label(port_frame, text="-").pack(side=tk.LEFT)
        ttk.Entry(port_frame, width=6, textvariable=self.port_end_var).pack(side=tk.LEFT)
        
        # Timeout de varredura
        ttk.Label(scan_frame, text="Timeout de Varredura (ms):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        timeout_var = tk.StringVar(value="1000")
        ttk.Entry(scan_frame, width=8, textvariable=timeout_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Configurações de interface
        ui_frame = ttk.LabelFrame(settings_frame, text="Configurações de Interface", padding=10)
        ui_frame.pack(fill=tk.X, pady=5)
        
        # Tema
        ttk.Label(ui_frame, text="Tema:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        theme_var = tk.StringVar(value="Claro")
        theme_combo = ttk.Combobox(ui_frame, textvariable=theme_var, state="readonly", width=15)
        theme_combo["values"] = ("Claro", "Escuro", "Sistema")
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Tamanho da fonte
        ttk.Label(ui_frame, text="Tamanho da Fonte:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        font_size_var = tk.StringVar(value="Normal")
        font_size_combo = ttk.Combobox(ui_frame, textvariable=font_size_var, state="readonly", width=15)
        font_size_combo["values"] = ("Pequeno", "Normal", "Grande")
        font_size_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Configurações avançadas
        advanced_frame = ttk.LabelFrame(settings_frame, text="Configurações Avançadas", padding=10)
        advanced_frame.pack(fill=tk.X, pady=5)
        
        # Método de varredura
        ttk.Label(advanced_frame, text="Método de Varredura:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        scan_method_var = tk.StringVar(value="Automático")
        scan_method_combo = ttk.Combobox(advanced_frame, textvariable=scan_method_var, state="readonly", width=15)
        scan_method_combo["values"] = ("Automático", "ARP", "Ping")
        scan_method_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Número de threads
        ttk.Label(advanced_frame, text="Número de Threads:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        threads_var = tk.StringVar(value="100")
        ttk.Entry(advanced_frame, width=8, textvariable=threads_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Frame para botões
        button_frame = ttk.Frame(settings_window, padding=10)
        button_frame.pack(fill=tk.X)
        
        # Botão para salvar
        save_button = ttk.Button(button_frame, text="Salvar", command=settings_window.destroy)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # Botão para cancelar
        cancel_button = ttk.Button(button_frame, text="Cancelar", command=settings_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def show_network_visualization(self):
        """Exibe a aba de visualização da rede."""
        self.notebook.select(self.visualization_frame)
        self.update_network_visualization()
    
    def show_help(self):
        """Exibe a ajuda da aplicação."""
        help_text = """
        Mini Ferramenta de Varredura de Rede
        
        Esta ferramenta permite descobrir dispositivos na sua rede local e verificar portas abertas.
        
        Funcionalidades:
        - Descoberta de dispositivos na rede local
        - Verificação de portas abertas
        - Resolução de nomes de dispositivos
        - Visualização gráfica da rede
        - Histórico de varreduras
        - Exportação de resultados
        
        Como usar:
        1. Clique em "Iniciar Varredura" para descobrir dispositivos na rede
        2. Selecione um dispositivo na tabela para ver detalhes
        3. Clique em "Verificar Portas" para verificar portas abertas no dispositivo selecionado
        4. Use o menu "Arquivo" para salvar ou exportar os resultados
        5. Use o menu "Histórico" para gerenciar varreduras anteriores
        6. Use a aba "Visualização" para ver uma representação gráfica da rede
        
        Observações:
        - A varredura de rede pode levar algum tempo, dependendo do tamanho da rede
        - A verificação de portas pode ser detectada por firewalls e sistemas de segurança
        - Use esta ferramenta apenas em redes que você tem permissão para analisar
        """
        
        # Cria uma janela para a ajuda
        help_window = tk.Toplevel(self.root)
        help_window.title("Ajuda")
        help_window.geometry("600x500")
        help_window.minsize(600, 500)
        help_window.transient(self.root)
        
        # Frame para o texto de ajuda
        help_frame = ttk.Frame(help_window, padding=10)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        # Texto de ajuda
        help_text_widget = tk.Text(help_frame, wrap=tk.WORD, font=("Segoe UI", 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(help_text_widget, command=help_text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text_widget.config(yscrollcommand=scrollbar.set)
        
        # Botão para fechar
        close_button = ttk.Button(help_window, text="Fechar", command=help_window.destroy)
        close_button.pack(pady=10)
    
    def show_about(self):
        """Exibe informações sobre a aplicação."""
        about_text = """
        Mini Ferramenta de Varredura de Rede
        
        Versão 1.0
        
        Uma ferramenta para descobrir dispositivos na rede local e verificar portas abertas.
        
        Desenvolvido com Python e Tkinter.
        
        Bibliotecas utilizadas:
        - socket: Para comunicação de rede
        - scapy: Para funcionalidades avançadas de varredura
        - subprocess: Para executar comandos do sistema
        - threading: Para operações paralelas
        - tkinter: Para a interface gráfica
        
        © 2025 - Todos os direitos reservados
        """
        
        # Cria uma janela para as informações
        about_window = tk.Toplevel(self.root)
        about_window.title("Sobre")
        about_window.geometry("400x300")
        about_window.minsize(400, 300)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Frame para as informações
        about_frame = ttk.Frame(about_window, padding=10)
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(about_frame, text="Mini Ferramenta de Varredura de Rede", font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=10)
        
        # Texto sobre a aplicação
        about_text_widget = tk.Text(about_frame, wrap=tk.WORD, font=("Segoe UI", 10), height=10)
        about_text_widget.pack(fill=tk.BOTH, expand=True)
        about_text_widget.insert(tk.END, about_text)
        about_text_widget.config(state=tk.DISABLED)
        
        # Botão para fechar
        close_button = ttk.Button(about_window, text="Fechar", command=about_window.destroy)
        close_button.pack(pady=10)
    
    def check_scan_status(self):
        """Verifica periodicamente o status da varredura."""
        # Atualiza o status da varredura
        if self.scan_running:
            # Atualiza a barra de progresso (simulação)
            current = self.progress_var.get()
            if current < 90:  # Limita a 90% para que a conclusão real chegue a 100%
                self.progress_var.set(current + 1)
        
        # Agenda a próxima verificação
        self.root.after(100, self.check_scan_status)
    
    def on_close(self):
        """Manipula o fechamento da janela."""
        # Interrompe qualquer varredura em andamento
        if self.scan_running:
            self.stop_scan()
        
        # Fecha a aplicação
        self.root.destroy()


# Função para iniciar a aplicação
def main():
    """Função principal para iniciar a aplicação."""
    # Cria a janela principal
    root = tk.Tk()
    
    # Cria a aplicação
    app = NetworkScannerGUI(root)
    
    # Inicia o loop principal
    root.mainloop()


# Ponto de entrada
if __name__ == "__main__":
    # Importa o módulo math para cálculos na visualização
    import math
    
    # Inicia a aplicação
    main()
