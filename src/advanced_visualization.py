#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Integração de Visualizações Avançadas
----------------------------------------------
Este módulo integra as visualizações 3D e geoespacial à interface principal.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys

# Importa os módulos de visualização
try:
    from .network_3d_visualizer import Network3DVisualizer
    from .geospatial_visualizer import GeoSpatialVisualizer
except ImportError:
    try:
        from network_3d_visualizer import Network3DVisualizer
        from geospatial_visualizer import GeoSpatialVisualizer
    except ImportError:
        print("Erro ao importar módulos de visualização. Verifique se os arquivos estão no mesmo diretório.")

class AdvancedVisualizationManager:
    """Classe para gerenciar visualizações avançadas da rede."""
    
    def __init__(self, parent_gui):
        """
        Inicializa o gerenciador de visualizações avançadas.
        
        Args:
            parent_gui: Referência à interface gráfica principal
        """
        self.parent_gui = parent_gui
        self.scanner = parent_gui.scanner
        
        # Inicializa os visualizadores
        try:
            self.network_3d_visualizer = Network3DVisualizer()
            self.geospatial_visualizer = GeoSpatialVisualizer()
            self.visualizers_available = True
        except Exception as e:
            print(f"Erro ao inicializar visualizadores: {e}")
            self.visualizers_available = False
        
        # Cria a interface para visualizações avançadas
        self.create_advanced_visualization_tab()
    
    def create_advanced_visualization_tab(self):
        """Cria a aba de visualizações avançadas na interface."""
        # Cria a aba de visualizações avançadas
        self.advanced_vis_frame = ttk.Frame(self.parent_gui.notebook, padding=10)
        self.parent_gui.notebook.add(self.advanced_vis_frame, text="Visualizações Avançadas")
        
        # Título
        ttk.Label(self.advanced_vis_frame, text="Visualizações Avançadas da Rede", 
                 font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Descrição
        description = (
            "Explore sua rede com visualizações avançadas que oferecem novas perspectivas "
            "sobre a topologia e distribuição geográfica dos dispositivos."
        )
        ttk.Label(self.advanced_vis_frame, text=description, wraplength=600).pack(pady=10)
        
        # Frame para os botões de visualização
        buttons_frame = ttk.Frame(self.advanced_vis_frame)
        buttons_frame.pack(pady=20)
        
        # Botão para visualização 3D
        self.vis_3d_button = ttk.Button(
            buttons_frame, 
            text="Visualização 3D da Rede", 
            command=self.show_3d_visualization,
            width=25
        )
        self.vis_3d_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Descrição da visualização 3D
        vis_3d_desc = (
            "Visualize a topologia da sua rede em um ambiente tridimensional interativo, "
            "permitindo rotação, zoom e exploração da estrutura de conexões."
        )
        ttk.Label(buttons_frame, text=vis_3d_desc, wraplength=400).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Botão para visualização geoespacial
        self.vis_geo_button = ttk.Button(
            buttons_frame, 
            text="Visualização Geoespacial", 
            command=self.show_geospatial_visualization,
            width=25
        )
        self.vis_geo_button.grid(row=1, column=0, padx=10, pady=10)
        
        # Descrição da visualização geoespacial
        vis_geo_desc = (
            "Veja a distribuição geográfica dos dispositivos da sua rede em um mapa interativo, "
            "com informações detalhadas sobre cada dispositivo."
        )
        ttk.Label(buttons_frame, text=vis_geo_desc, wraplength=400).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Status das visualizações
        self.vis_status_label = ttk.Label(self.advanced_vis_frame, text="")
        self.vis_status_label.pack(pady=10)
        
        # Verifica se os visualizadores estão disponíveis
        if not self.visualizers_available:
            self.vis_status_label.config(
                text="Algumas dependências para visualizações avançadas não estão disponíveis.",
                foreground="red"
            )
            self.vis_3d_button.config(state=tk.DISABLED)
            self.vis_geo_button.config(state=tk.DISABLED)
    
    def show_3d_visualization(self):
        """Exibe a visualização 3D da rede."""
        # Verifica se há resultados de varredura
        if not self.scanner.scan_results:
            messagebox.showinfo("Sem Dados", "Execute uma varredura de rede primeiro para visualizar os resultados em 3D.")
            return
        
        # Atualiza o status
        self.vis_status_label.config(text="Gerando visualização 3D... Por favor, aguarde.", foreground="blue")
        self.parent_gui.update_status("Gerando visualização 3D da rede...")
        
        # Desabilita os botões durante o processamento
        self.vis_3d_button.config(state=tk.DISABLED)
        self.vis_geo_button.config(state=tk.DISABLED)
        
        # Cria uma thread para não bloquear a interface
        threading.Thread(target=self._generate_3d_visualization, daemon=True).start()
    
    def _generate_3d_visualization(self):
        """Gera a visualização 3D em uma thread separada."""
        try:
            # Constrói o grafo da rede
            self.network_3d_visualizer.build_network_graph(
                self.scanner.scan_results,
                self.scanner.local_ip,
                self.scanner.gateway
            )
            
            # Cria a visualização
            html_file = self.network_3d_visualizer.create_3d_visualization("Visualização 3D da Rede")
            
            # Abre a visualização no navegador
            self.network_3d_visualizer.open_visualization(html_file)
            
            # Atualiza o status na thread principal
            self.parent_gui.root.after(0, lambda: self._update_vis_status(
                "Visualização 3D gerada com sucesso e aberta no navegador.", "green"
            ))
        except Exception as e:
            # Atualiza o status com o erro na thread principal
            self.parent_gui.root.after(0, lambda: self._update_vis_status(
                f"Erro ao gerar visualização 3D: {e}", "red"
            ))
    
    def show_geospatial_visualization(self):
        """Exibe a visualização geoespacial da rede."""
        # Verifica se há resultados de varredura
        if not self.scanner.scan_results:
            messagebox.showinfo("Sem Dados", "Execute uma varredura de rede primeiro para visualizar os resultados no mapa.")
            return
        
        # Atualiza o status
        self.vis_status_label.config(text="Gerando visualização geoespacial... Por favor, aguarde.", foreground="blue")
        self.parent_gui.update_status("Gerando visualização geoespacial da rede...")
        
        # Desabilita os botões durante o processamento
        self.vis_3d_button.config(state=tk.DISABLED)
        self.vis_geo_button.config(state=tk.DISABLED)
        
        # Cria uma thread para não bloquear a interface
        threading.Thread(target=self._generate_geospatial_visualization, daemon=True).start()
    
    def _generate_geospatial_visualization(self):
        """Gera a visualização geoespacial em uma thread separada."""
        try:
            # Cria a visualização
            html_file = self.geospatial_visualizer.create_geospatial_visualization(
                self.scanner.scan_results,
                self.scanner.local_ip,
                self.scanner.gateway,
                "Visualização Geoespacial da Rede"
            )
            
            # Abre a visualização no navegador
            self.geospatial_visualizer.open_visualization(html_file)
            
            # Atualiza o status na thread principal
            self.parent_gui.root.after(0, lambda: self._update_vis_status(
                "Visualização geoespacial gerada com sucesso e aberta no navegador.", "green"
            ))
        except Exception as e:
            # Atualiza o status com o erro na thread principal
            self.parent_gui.root.after(0, lambda: self._update_vis_status(
                f"Erro ao gerar visualização geoespacial: {e}", "red"
            ))
    
    def _update_vis_status(self, message, color):
        """
        Atualiza o status das visualizações na interface.
        
        Args:
            message: Mensagem de status
            color: Cor do texto
        """
        self.vis_status_label.config(text=message, foreground=color)
        self.parent_gui.update_status(message)
        
        # Reabilita os botões
        self.vis_3d_button.config(state=tk.NORMAL)
        self.vis_geo_button.config(state=tk.NORMAL)
