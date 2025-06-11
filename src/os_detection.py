#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Detecção de Sistema Operacional
----------------------------------------
Este módulo contém funções para detectar o sistema operacional dos dispositivos na rede
baseado em técnicas como análise de TTL, portas abertas e banners de serviços.
"""

import socket
import re
import subprocess
import platform
import time
from collections import Counter

class OSDetector:
    """Classe para detecção de sistema operacional de dispositivos na rede."""
    
    def __init__(self):
        """Inicializa o detector de sistema operacional."""
        # Dicionário de TTLs comuns por sistema operacional
        self.ttl_signatures = {
            64: ["Linux", "Unix", "macOS", "iOS"],
            128: ["Windows"],
            254: ["Solaris", "AIX"],
            255: ["FreeBSD", "Network Equipment"]
        }
        
        # Dicionário de portas comuns por sistema operacional
        self.os_port_signatures = {
            "Windows": [135, 139, 445, 3389],
            "Linux": [22, 111, 2049],
            "macOS": [22, 548, 5009, 7000],
            "FreeBSD": [22, 80],
            "Network Equipment": [22, 23, 80, 443]
        }
        
        # Expressões regulares para identificar sistemas operacionais em banners
        self.banner_signatures = {
            "Windows": [
                re.compile(r'Microsoft|Windows', re.IGNORECASE),
                re.compile(r'IIS', re.IGNORECASE)
            ],
            "Linux": [
                re.compile(r'Linux|Ubuntu|Debian|CentOS|Fedora|Red Hat|RHEL', re.IGNORECASE),
                re.compile(r'Apache', re.IGNORECASE)
            ],
            "macOS": [
                re.compile(r'Mac OS|macOS|Darwin', re.IGNORECASE)
            ],
            "FreeBSD": [
                re.compile(r'FreeBSD|OpenBSD|NetBSD', re.IGNORECASE)
            ],
            "Network Equipment": [
                re.compile(r'Cisco|Juniper|Huawei|Mikrotik|RouterOS', re.IGNORECASE)
            ]
        }
    
    def detect_os_by_ttl(self, ip):
        """
        Detecta o sistema operacional baseado no valor TTL.
        
        Args:
            ip: Endereço IP do dispositivo
            
        Returns:
            tuple: (ttl, lista_de_sistemas_operacionais_possiveis)
        """
        ttl = self._get_ttl(ip)
        if ttl is None:
            return None, ["Desconhecido"]
        
        # Encontra o TTL base mais próximo
        base_ttl = None
        for base in sorted(self.ttl_signatures.keys()):
            if ttl <= base:
                base_ttl = base
                break
        
        # Se não encontrou um TTL base, usa o maior
        if base_ttl is None:
            base_ttl = max(self.ttl_signatures.keys())
        
        # Retorna o TTL e os possíveis sistemas operacionais
        return ttl, self.ttl_signatures.get(base_ttl, ["Desconhecido"])
    
    def _get_ttl(self, ip):
        """
        Obtém o valor TTL de um dispositivo usando ping.
        
        Args:
            ip: Endereço IP do dispositivo
            
        Returns:
            int: Valor TTL ou None se não for possível obter
        """
        try:
            # Comando ping específico para Windows
            if platform.system() == "Windows":
                ping_cmd = f"ping -n 1 {ip}"
                output = subprocess.check_output(ping_cmd, shell=True).decode()
                
                # Procura pelo valor TTL na saída
                ttl_match = re.search(r'TTL=(\d+)', output, re.IGNORECASE)
                if ttl_match:
                    return int(ttl_match.group(1))
            else:
                # Para outros sistemas, usa um comando diferente
                ping_cmd = f"ping -c 1 {ip}"
                output = subprocess.check_output(ping_cmd, shell=True).decode()
                
                # Procura pelo valor TTL na saída
                ttl_match = re.search(r'ttl=(\d+)', output, re.IGNORECASE)
                if ttl_match:
                    return int(ttl_match.group(1))
        except:
            pass
        
        return None
    
    def detect_os_by_ports(self, ip, open_ports):
        """
        Detecta o sistema operacional baseado nas portas abertas.
        
        Args:
            ip: Endereço IP do dispositivo
            open_ports: Lista de portas abertas
            
        Returns:
            dict: Dicionário com pontuação para cada sistema operacional
        """
        if not open_ports:
            return {}
        
        scores = {}
        
        # Calcula a pontuação para cada sistema operacional
        for os_name, signature_ports in self.os_port_signatures.items():
            # Conta quantas portas da assinatura estão abertas
            matches = sum(1 for port in signature_ports if port in open_ports)
            
            # Calcula a pontuação como porcentagem de correspondência
            if matches > 0:
                score = (matches / len(signature_ports)) * 100
                scores[os_name] = score
        
        return scores
    
    def get_service_banner(self, ip, port, timeout=1):
        """
        Tenta obter o banner de um serviço.
        
        Args:
            ip: Endereço IP do dispositivo
            port: Número da porta
            timeout: Tempo limite em segundos
            
        Returns:
            str: Banner do serviço ou None se não for possível obter
        """
        try:
            # Cria um socket e tenta conectar à porta
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip, port))
            
            # Espera um pouco para receber dados
            time.sleep(0.2)
            
            # Tenta receber o banner
            banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
            s.close()
            
            return banner if banner else None
        except:
            return None
    
    def detect_os_by_banners(self, ip, open_ports):
        """
        Detecta o sistema operacional baseado nos banners dos serviços.
        
        Args:
            ip: Endereço IP do dispositivo
            open_ports: Lista de portas abertas
            
        Returns:
            dict: Dicionário com pontuação para cada sistema operacional
        """
        if not open_ports:
            return {}
        
        scores = {}
        banners = {}
        
        # Portas comuns para tentar obter banners
        common_banner_ports = [21, 22, 23, 25, 80, 110, 143, 443, 8080]
        
        # Filtra as portas para verificar
        ports_to_check = [port for port in open_ports if port in common_banner_ports]
        
        # Limita a 5 portas para não demorar muito
        ports_to_check = ports_to_check[:5]
        
        # Obtém os banners
        for port in ports_to_check:
            banner = self.get_service_banner(ip, port)
            if banner:
                banners[port] = banner
        
        # Se não obteve nenhum banner, retorna vazio
        if not banners:
            return {}
        
        # Analisa os banners para cada sistema operacional
        for os_name, patterns in self.banner_signatures.items():
            matches = 0
            
            # Verifica cada banner contra os padrões
            for banner in banners.values():
                for pattern in patterns:
                    if pattern.search(banner):
                        matches += 1
                        break
            
            # Calcula a pontuação
            if matches > 0:
                score = (matches / len(banners)) * 100
                scores[os_name] = score
        
        return scores
    
    def detect_os(self, ip, open_ports=None):
        """
        Detecta o sistema operacional usando múltiplas técnicas.
        
        Args:
            ip: Endereço IP do dispositivo
            open_ports: Lista de portas abertas (opcional)
            
        Returns:
            dict: Informações sobre o sistema operacional detectado
        """
        result = {
            'os': "Desconhecido",
            'confidence': 0,
            'details': {
                'ttl': None,
                'ttl_os': [],
                'port_scores': {},
                'banner_scores': {}
            }
        }
        
        # Detecta por TTL
        ttl, ttl_os = self.detect_os_by_ttl(ip)
        result['details']['ttl'] = ttl
        result['details']['ttl_os'] = ttl_os
        
        # Se tiver portas abertas, detecta por portas e banners
        if open_ports:
            # Converte para lista se for dicionário
            if isinstance(open_ports, dict):
                open_ports = list(open_ports.keys())
            
            # Detecta por portas
            port_scores = self.detect_os_by_ports(ip, open_ports)
            result['details']['port_scores'] = port_scores
            
            # Detecta por banners
            banner_scores = self.detect_os_by_banners(ip, open_ports)
            result['details']['banner_scores'] = banner_scores
            
            # Combina os resultados
            combined_scores = {}
            
            # Adiciona pontuação do TTL
            for os_name in ttl_os:
                combined_scores[os_name] = combined_scores.get(os_name, 0) + 40  # TTL tem peso 40%
            
            # Adiciona pontuação das portas
            for os_name, score in port_scores.items():
                combined_scores[os_name] = combined_scores.get(os_name, 0) + (score * 0.3)  # Portas têm peso 30%
            
            # Adiciona pontuação dos banners
            for os_name, score in banner_scores.items():
                combined_scores[os_name] = combined_scores.get(os_name, 0) + (score * 0.3)  # Banners têm peso 30%
            
            # Encontra o sistema operacional com maior pontuação
            if combined_scores:
                best_os = max(combined_scores.items(), key=lambda x: x[1])
                result['os'] = best_os[0]
                result['confidence'] = min(best_os[1], 100)  # Limita a confiança a 100%
        else:
            # Se não tiver portas, usa apenas o TTL
            if ttl_os and ttl_os[0] != "Desconhecido":
                result['os'] = ttl_os[0]
                result['confidence'] = 40  # Confiança baixa, apenas com TTL
        
        return result

# Função para teste do módulo
if __name__ == "__main__":
    detector = OSDetector()
    
    # Testa a detecção em localhost
    ip = "127.0.0.1"
    print(f"Detectando SO de {ip}...")
    
    # Detecta por TTL
    ttl, ttl_os = detector.detect_os_by_ttl(ip)
    print(f"TTL: {ttl}, Possíveis SOs: {ttl_os}")
    
    # Detecta com todas as técnicas
    result = detector.detect_os(ip)
    print(f"Sistema Operacional: {result['os']} (Confiança: {result['confidence']:.1f}%)")
    print(f"Detalhes: {result['details']}")
