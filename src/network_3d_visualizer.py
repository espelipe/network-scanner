#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Visualização 3D da Rede
---------------------------------
Este módulo contém as funcionalidades para visualização 3D da topologia de rede
usando Plotly para gráficos interativos.
"""

import plotly.graph_objects as go
import networkx as nx
import numpy as np
import webbrowser
import os
import tempfile
import random
import math
from plotly.offline import plot

class Network3DVisualizer:
    """Classe para visualização 3D da topologia de rede."""
    
    def __init__(self):
        """Inicializa o visualizador 3D."""
        self.graph = nx.Graph()
        self.node_positions = {}
        self.node_colors = {}
        self.node_sizes = {}
        self.node_labels = {}
        self.edge_colors = {}
        
        # Cores padrão
        self.default_colors = {
            'gateway': '#FFD700',  # Dourado para o gateway
            'local': '#90EE90',    # Verde claro para o dispositivo local
            'device': '#6495ED',   # Azul para dispositivos normais
            'edge': '#CCCCCC'      # Cinza claro para conexões
        }
        
        # Tamanhos padrão
        self.default_sizes = {
            'gateway': 15,
            'local': 12,
            'device': 10
        }
    
    def build_network_graph(self, scan_results, local_ip, gateway_ip):
        """
        Constrói o grafo da rede a partir dos resultados da varredura.
        
        Args:
            scan_results: Dicionário com os resultados da varredura
            local_ip: IP do dispositivo local
            gateway_ip: IP do gateway
        """
        # Limpa o grafo anterior
        self.graph.clear()
        self.node_positions = {}
        self.node_colors = {}
        self.node_sizes = {}
        self.node_labels = {}
        self.edge_colors = {}
        
        # Adiciona os nós ao grafo
        for ip, device_data in scan_results.items():
            # Determina o tipo de dispositivo
            if ip == gateway_ip:
                node_type = 'gateway'
                label = f"Gateway\n{ip}"
            elif ip == local_ip:
                node_type = 'local'
                label = f"Este PC\n{ip}"
            else:
                node_type = 'device'
                hostname = device_data.get('hostname')
                if hostname:
                    label = f"{hostname.split('.')[0]}\n{ip}"
                else:
                    label = f"Dispositivo\n{ip}"
            
            # Adiciona o nó ao grafo
            self.graph.add_node(ip)
            
            # Define a cor do nó
            self.node_colors[ip] = self.default_colors[node_type]
            
            # Define o tamanho do nó (baseado no número de portas abertas)
            ports = device_data.get('ports', {})
            port_count = len(ports)
            base_size = self.default_sizes[node_type]
            self.node_sizes[ip] = base_size + min(port_count, 10)  # Limita o crescimento
            
            # Define o rótulo do nó
            self.node_labels[ip] = label
            
            # Adiciona aresta ao gateway (exceto para o próprio gateway)
            if ip != gateway_ip and gateway_ip in scan_results:
                self.graph.add_edge(ip, gateway_ip)
                self.edge_colors[(ip, gateway_ip)] = self.default_colors['edge']
        
        # Gera posições 3D para os nós
        self._generate_3d_positions()
    
    def _generate_3d_positions(self):
        """Gera posições 3D para os nós do grafo."""
        # Usa o algoritmo de layout spring para posicionamento inicial
        pos_2d = nx.spring_layout(self.graph, seed=42)
        
        # Converte para posições 3D
        for node, pos in pos_2d.items():
            # Adiciona uma coordenada Z com alguma variação
            z = 0.1 + 0.2 * random.random()
            
            # Para o gateway, coloca no topo
            if node == list(self.node_colors.keys())[list(self.node_colors.values()).index(self.default_colors['gateway'])]:
                z = 0.5
            
            self.node_positions[node] = (pos[0], pos[1], z)
    
    def create_3d_visualization(self, title="Visualização 3D da Rede"):
        """
        Cria a visualização 3D da rede.
        
        Args:
            title: Título da visualização
            
        Returns:
            str: Caminho para o arquivo HTML da visualização
        """
        # Prepara os dados para o Plotly
        node_x = []
        node_y = []
        node_z = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in self.graph.nodes():
            x, y, z = self.node_positions[node]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            node_text.append(self.node_labels[node])
            node_color.append(self.node_colors[node])
            node_size.append(self.node_sizes[node])
        
        # Cria o gráfico de nós
        node_trace = go.Scatter3d(
            x=node_x,
            y=node_y,
            z=node_z,
            mode='markers+text',
            text=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                opacity=0.8,
                line=dict(width=1, color='#000000')
            ),
            textposition="top center"
        )
        
        # Prepara os dados das arestas
        edge_x = []
        edge_y = []
        edge_z = []
        edge_color = []
        
        for edge in self.graph.edges():
            x0, y0, z0 = self.node_positions[edge[0]]
            x1, y1, z1 = self.node_positions[edge[1]]
            
            # Adiciona os pontos para a linha
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])
            
            # Cor da aresta
            color = self.edge_colors.get(edge, self.edge_colors.get((edge[1], edge[0]), self.default_colors['edge']))
            edge_color.extend([color, color, color])
        
        # Cria o gráfico de arestas
        edge_trace = go.Scatter3d(
            x=edge_x,
            y=edge_y,
            z=edge_z,
            mode='lines',
            line=dict(color=edge_color, width=2),
            hoverinfo='none'
        )
        
        # Cria a figura
        fig = go.Figure(data=[edge_trace, node_trace])
        
        # Configura o layout
        fig.update_layout(
            title=title,
            showlegend=False,
            scene=dict(
                xaxis=dict(showticklabels=False, title=''),
                yaxis=dict(showticklabels=False, title=''),
                zaxis=dict(showticklabels=False, title=''),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            hovermode='closest',
            template='plotly_white'
        )
        
        # Adiciona legenda personalizada
        annotations = [
            dict(
                x=0.01, y=0.99, xref="paper", yref="paper",
                text="Gateway", showarrow=False,
                font=dict(size=12), bgcolor=self.default_colors['gateway'],
                bordercolor="black", borderwidth=1, borderpad=4
            ),
            dict(
                x=0.01, y=0.94, xref="paper", yref="paper",
                text="Este PC", showarrow=False,
                font=dict(size=12), bgcolor=self.default_colors['local'],
                bordercolor="black", borderwidth=1, borderpad=4
            ),
            dict(
                x=0.01, y=0.89, xref="paper", yref="paper",
                text="Dispositivo", showarrow=False,
                font=dict(size=12), bgcolor=self.default_colors['device'],
                bordercolor="black", borderwidth=1, borderpad=4
            )
        ]
        
        fig.update_layout(annotations=annotations)
        
        # Salva a visualização em um arquivo HTML temporário
        temp_dir = tempfile.gettempdir()
        html_file = os.path.join(temp_dir, "network_3d_visualization.html")
        
        # Configura para incluir todos os recursos necessários no HTML
        plot(fig, filename=html_file, auto_open=False, include_plotlyjs=True)
        
        return html_file
    
    def open_visualization(self, html_file):
        """
        Abre a visualização 3D no navegador padrão.
        
        Args:
            html_file: Caminho para o arquivo HTML da visualização
        """
        webbrowser.open(f"file://{html_file}")

# Função para teste do módulo
if __name__ == "__main__":
    # Cria um visualizador
    visualizer = Network3DVisualizer()
    
    # Cria dados de teste
    test_results = {
        "192.168.1.1": {"hostname": "router.local", "ports": {80: "HTTP", 443: "HTTPS", 22: "SSH"}},
        "192.168.1.2": {"hostname": "pc1.local", "ports": {445: "SMB"}},
        "192.168.1.3": {"hostname": "pc2.local", "ports": {80: "HTTP"}},
        "192.168.1.4": {"hostname": "printer.local", "ports": {9100: "Printer"}},
        "192.168.1.5": {"hostname": "nas.local", "ports": {80: "HTTP", 443: "HTTPS", 22: "SSH", 445: "SMB"}}
    }
    
    # Constrói o grafo
    visualizer.build_network_graph(test_results, "192.168.1.2", "192.168.1.1")
    
    # Cria e abre a visualização
    html_file = visualizer.create_3d_visualization("Teste de Visualização 3D")
    visualizer.open_visualization(html_file)
