#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Visualização Geoespacial da Rede
-----------------------------------------
Este módulo contém as funcionalidades para visualização geoespacial da rede
usando Folium para mapas interativos.
"""

import folium
import requests
import json
import os
import tempfile
import webbrowser
import ipaddress
import random
from folium.plugins import MarkerCluster

class GeoSpatialVisualizer:
    """Classe para visualização geoespacial da rede."""
    
    def __init__(self):
        """Inicializa o visualizador geoespacial."""
        self.ip_locations = {}
        self.default_location = [0, 0]  # Localização padrão (será ajustada)
        self.local_network_radius = 0.001  # Raio para dispositivos locais sem geolocalização
        
        # Cores padrão
        self.device_colors = {
            'gateway': 'gold',
            'local': 'green',
            'device': 'blue',
            'unknown': 'gray'
        }
        
        # Ícones padrão
        self.device_icons = {
            'gateway': 'globe',
            'local': 'home',
            'device': 'server',
            'unknown': 'question-sign'
        }
    
    def get_ip_geolocation(self, ip):
        """
        Obtém a geolocalização de um endereço IP.
        
        Args:
            ip: Endereço IP para geolocalização
            
        Returns:
            tuple: (latitude, longitude) ou None se não for possível obter
        """
        # Verifica se é um IP privado
        try:
            if ipaddress.ip_address(ip).is_private:
                return None
        except:
            return None
        
        # Verifica se já temos a localização em cache
        if ip in self.ip_locations:
            return self.ip_locations[ip]
        
        try:
            # Usa a API ipinfo.io para obter a geolocalização
            response = requests.get(f"https://ipinfo.io/{ip}/json")
            if response.status_code == 200:
                data = response.json()
                if 'loc' in data:
                    # O formato é "latitude,longitude"
                    lat, lon = map(float, data['loc'].split(','))
                    self.ip_locations[ip] = (lat, lon)
                    return (lat, lon)
        except Exception as e:
            print(f"Erro ao obter geolocalização para {ip}: {e}")
        
        return None
    
    def create_geospatial_visualization(self, scan_results, local_ip, gateway_ip, title="Visualização Geoespacial da Rede"):
        """
        Cria a visualização geoespacial da rede.
        
        Args:
            scan_results: Dicionário com os resultados da varredura
            local_ip: IP do dispositivo local
            gateway_ip: IP do gateway
            title: Título da visualização
            
        Returns:
            str: Caminho para o arquivo HTML da visualização
        """
        # Obtém a localização do IP público
        public_ip = self.get_public_ip()
        public_location = self.get_ip_geolocation(public_ip)
        
        # Define a localização central do mapa
        if public_location:
            self.default_location = public_location
        
        # Cria o mapa
        m = folium.Map(location=self.default_location, zoom_start=10, 
                      tiles="OpenStreetMap", control_scale=True)
        
        # Adiciona título
        title_html = f'''
            <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Cria um cluster para dispositivos locais
        local_cluster = MarkerCluster(name="Dispositivos Locais")
        
        # Adiciona o gateway
        if gateway_ip in scan_results:
            self.add_device_to_map(m, local_cluster, gateway_ip, scan_results[gateway_ip], 
                                  'gateway', local_ip, gateway_ip)
        
        # Adiciona o dispositivo local
        if local_ip in scan_results:
            self.add_device_to_map(m, local_cluster, local_ip, scan_results[local_ip], 
                                  'local', local_ip, gateway_ip)
        
        # Adiciona os demais dispositivos
        for ip, device_data in scan_results.items():
            if ip != gateway_ip and ip != local_ip:
                self.add_device_to_map(m, local_cluster, ip, device_data, 
                                      'device', local_ip, gateway_ip)
        
        # Adiciona o cluster ao mapa
        m.add_child(local_cluster)
        
        # Adiciona controle de camadas
        folium.LayerControl().add_to(m)
        
        # Adiciona legenda
        legend_html = self.create_legend()
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Salva o mapa em um arquivo HTML temporário
        temp_dir = tempfile.gettempdir()
        html_file = os.path.join(temp_dir, "network_geospatial_visualization.html")
        m.save(html_file)
        
        return html_file
    
    def add_device_to_map(self, map_obj, cluster, ip, device_data, device_type, local_ip, gateway_ip):
        """
        Adiciona um dispositivo ao mapa.
        
        Args:
            map_obj: Objeto do mapa Folium
            cluster: Cluster para dispositivos locais
            ip: Endereço IP do dispositivo
            device_data: Dados do dispositivo
            device_type: Tipo do dispositivo ('gateway', 'local', 'device')
            local_ip: IP do dispositivo local
            gateway_ip: IP do gateway
        """
        # Obtém a geolocalização do IP
        location = self.get_ip_geolocation(ip)
        
        # Se não conseguiu obter a geolocalização, usa uma localização próxima ao padrão
        if not location:
            # Gera uma localização aleatória próxima ao centro para dispositivos locais
            lat = self.default_location[0] + (random.random() - 0.5) * self.local_network_radius
            lon = self.default_location[1] + (random.random() - 0.5) * self.local_network_radius
            location = (lat, lon)
        
        # Prepara o popup com informações do dispositivo
        hostname = device_data.get('hostname', 'Desconhecido')
        mac = device_data.get('mac', 'Desconhecido')
        os_info = device_data.get('os', {}).get('name', 'Desconhecido')
        ports = device_data.get('ports', {})
        
        # Formata a lista de portas
        ports_str = '<br>'.join([f"Porta {port}: {service}" for port, service in list(ports.items())[:10]])
        if len(ports) > 10:
            ports_str += f"<br>... e mais {len(ports) - 10} portas"
        elif not ports:
            ports_str = "Nenhuma porta aberta detectada"
        
        # Cria o conteúdo do popup
        popup_content = f"""
        <div style="width: 250px;">
            <h4>{hostname}</h4>
            <b>IP:</b> {ip}<br>
            <b>MAC:</b> {mac}<br>
            <b>Sistema Operacional:</b> {os_info}<br>
            <b>Portas Abertas:</b><br>
            {ports_str}
        </div>
        """
        
        # Determina a cor e o ícone com base no tipo de dispositivo
        color = self.device_colors.get(device_type, self.device_colors['unknown'])
        icon = self.device_icons.get(device_type, self.device_icons['unknown'])
        
        # Cria o marcador
        marker = folium.Marker(
            location=location,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{hostname} ({ip})",
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
        )
        
        # Adiciona o marcador ao cluster para dispositivos locais
        cluster.add_child(marker)
    
    def create_legend(self):
        """
        Cria a legenda para o mapa.
        
        Returns:
            str: HTML da legenda
        """
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 150px; height: 120px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color: white; padding: 10px;
                    border-radius: 5px;">
            <p style="margin-top: 0;"><b>Legenda</b></p>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: gold; width: 15px; height: 15px; margin-right: 5px; border-radius: 50%;"></div>
                <span>Gateway</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: green; width: 15px; height: 15px; margin-right: 5px; border-radius: 50%;"></div>
                <span>Este PC</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="background-color: blue; width: 15px; height: 15px; margin-right: 5px; border-radius: 50%;"></div>
                <span>Dispositivo</span>
            </div>
        </div>
        '''
        return legend_html
    
    def get_public_ip(self):
        """
        Obtém o endereço IP público.
        
        Returns:
            str: Endereço IP público ou None se não for possível obter
        """
        try:
            response = requests.get('https://api.ipify.org?format=json')
            if response.status_code == 200:
                return response.json()['ip']
        except:
            pass
        
        try:
            response = requests.get('https://ifconfig.me/ip')
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        
        return None
    
    def open_visualization(self, html_file):
        """
        Abre a visualização geoespacial no navegador padrão.
        
        Args:
            html_file: Caminho para o arquivo HTML da visualização
        """
        webbrowser.open(f"file://{html_file}")

# Função para teste do módulo
if __name__ == "__main__":
    # Cria um visualizador
    visualizer = GeoSpatialVisualizer()
    
    # Cria dados de teste
    test_results = {
        "192.168.1.1": {"hostname": "router.local", "ports": {80: "HTTP", 443: "HTTPS", 22: "SSH"}},
        "192.168.1.2": {"hostname": "pc1.local", "ports": {445: "SMB"}},
        "192.168.1.3": {"hostname": "pc2.local", "ports": {80: "HTTP"}},
        "192.168.1.4": {"hostname": "printer.local", "ports": {9100: "Printer"}},
        "192.168.1.5": {"hostname": "nas.local", "ports": {80: "HTTP", 443: "HTTPS", 22: "SSH", 445: "SMB"}}
    }
    
    # Cria e abre a visualização
    html_file = visualizer.create_geospatial_visualization(test_results, "192.168.1.2", "192.168.1.1", "Teste de Visualização Geoespacial")
    visualizer.open_visualization(html_file)
