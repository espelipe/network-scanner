#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Varredura de Rede
---------------------------
Este módulo contém as funcionalidades para descoberta de dispositivos na rede local,
verificação de portas abertas e resolução de nomes de dispositivos.
"""

import socket
import subprocess
import threading
import ipaddress
import time
import platform
from queue import Queue
from datetime import datetime

# Importa o módulo de detecção de sistema operacional
try:
    from os_detection import OSDetector
except ImportError:
    print("Módulo de detecção de SO não encontrado. Esta funcionalidade não estará disponível.")

# Verificar se estamos no Windows para importar bibliotecas específicas
if platform.system() == "Windows":
    try:
        from scapy.all import ARP, Ether, srp
    except ImportError:
        print("Scapy não encontrado. Algumas funcionalidades podem não estar disponíveis.")

class NetworkScanner:
    """Classe principal para varredura de rede local."""
    
    def __init__(self):
        """Inicializa o scanner de rede."""
        self.local_ip = self.get_local_ip()
        self.gateway = self.get_gateway()
        self.network = self.get_network_from_ip(self.local_ip)
        self.scan_results = {}
        self.is_scanning = False
        self.stop_scan_flag = False
        
        # Inicializa o detector de sistema operacional
        try:
            self.os_detector = OSDetector()
        except NameError:
            self.os_detector = None
    
    def get_local_ip(self):
        """Obtém o endereço IP local da máquina."""
        try:
            # Cria uma conexão com um servidor externo para determinar o IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            # Fallback para localhost se não conseguir determinar o IP
            print(f"Erro ao obter IP local: {e}")
            return "127.0.0.1"
    
    def get_gateway(self):
        """Obtém o endereço IP do gateway padrão."""
        if platform.system() == "Windows":
            try:
                # Executa o comando route print para obter informações de roteamento
                output = subprocess.check_output("route print 0.0.0.0", shell=True).decode()
                lines = output.split('\n')
                for line in lines:
                    if "0.0.0.0" in line:
                        parts = line.split()
                        for part in parts:
                            if self.is_valid_ip(part) and part != "0.0.0.0":
                                return part
            except Exception as e:
                print(f"Erro ao obter gateway: {e}")
        return None
    
    def is_valid_ip(self, ip):
        """Verifica se uma string é um endereço IP válido."""
        try:
            socket.inet_aton(ip)
            return True
        except:
            return False
    
    def get_network_from_ip(self, ip):
        """Determina a rede a partir do IP local (assumindo /24)."""
        if not ip or ip == "127.0.0.1":
            return "192.168.1.0/24"  # Rede padrão se não conseguir determinar
        
        # Assume uma máscara de rede /24 para simplificar
        ip_parts = ip.split('.')
        network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return network
    
    def scan_network_arp(self, callback=None):
        """
        Varre a rede usando ARP requests (mais rápido, requer scapy).
        
        Args:
            callback: Função de callback para atualizar a interface com o progresso
        """
        if platform.system() != "Windows" or 'scapy.all' not in globals():
            print("Método ARP não disponível. Usando método de ping.")
            return self.scan_network_ping(callback)
        
        self.is_scanning = True
        self.stop_scan_flag = False
        self.scan_results = {}
        
        try:
            network = self.network
            print(f"Iniciando varredura ARP na rede {network}")
            
            # Cria pacote ARP
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            start_time = time.time()
            
            # Envia pacotes e recebe respostas
            result = srp(packet, timeout=3, verbose=0)[0]
            
            # Processa as respostas
            devices = []
            for sent, received in result:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})
            
            # Adiciona os dispositivos encontrados aos resultados
            for device in devices:
                ip = device['ip']
                self.scan_results[ip] = {
                    'mac': device['mac'],
                    'hostname': self.get_hostname(ip),
                    'ports': {},
                    'status': 'online',
                    'os': {'name': 'Desconhecido', 'confidence': 0}
                }
                if callback:
                    callback(ip, self.scan_results[ip])
            
            end_time = time.time()
            print(f"Varredura ARP concluída em {end_time - start_time:.2f} segundos")
            print(f"Encontrados {len(devices)} dispositivos")
            
        except Exception as e:
            print(f"Erro durante varredura ARP: {e}")
        finally:
            self.is_scanning = False
        
        return self.scan_results
    
    def scan_network_ping(self, callback=None):
        """
        Varre a rede usando ping (mais lento, mas funciona sem scapy).
        
        Args:
            callback: Função de callback para atualizar a interface com o progresso
        """
        self.is_scanning = True
        self.stop_scan_flag = False
        self.scan_results = {}
        
        try:
            # Obtém a rede a partir do IP local
            network = ipaddress.IPv4Network(self.network, strict=False)
            total_hosts = sum(1 for _ in network.hosts())
            
            print(f"Iniciando varredura de ping na rede {network}")
            print(f"Total de hosts a verificar: {total_hosts}")
            
            start_time = time.time()
            
            # Cria threads para fazer ping em paralelo
            q = Queue()
            threads = []
            num_threads = min(100, total_hosts)  # Limita o número de threads
            
            # Função que será executada por cada thread
            def ping_worker():
                while not self.stop_scan_flag:
                    try:
                        ip = q.get(block=False)
                    except:
                        break
                    
                    if self.ping(ip):
                        mac = self.get_mac_address(ip)
                        hostname = self.get_hostname(ip)
                        
                        self.scan_results[ip] = {
                            'mac': mac,
                            'hostname': hostname,
                            'ports': {},
                            'status': 'online',
                            'os': {'name': 'Desconhecido', 'confidence': 0}
                        }
                        
                        if callback:
                            callback(ip, self.scan_results[ip])
                    
                    q.task_done()
            
            # Adiciona todos os IPs à fila
            for host in network.hosts():
                q.put(str(host))
            
            # Inicia as threads
            for _ in range(num_threads):
                t = threading.Thread(target=ping_worker)
                t.daemon = True
                t.start()
                threads.append(t)
            
            # Espera a conclusão da varredura
            q.join()
            
            # Se a varredura foi interrompida, limpa as threads
            if self.stop_scan_flag:
                for _ in range(num_threads):
                    if not q.empty():
                        q.get()
                        q.task_done()
            
            end_time = time.time()
            print(f"Varredura de ping concluída em {end_time - start_time:.2f} segundos")
            print(f"Encontrados {len(self.scan_results)} dispositivos")
            
        except Exception as e:
            print(f"Erro durante varredura de ping: {e}")
        finally:
            self.is_scanning = False
        
        return self.scan_results
    
    def ping(self, ip):
        """
        Verifica se um host está online usando ping.
        
        Args:
            ip: Endereço IP a ser verificado
            
        Returns:
            bool: True se o host responder, False caso contrário
        """
        # Comando ping específico para Windows
        if platform.system() == "Windows":
            ping_cmd = f"ping -n 1 -w 1000 {ip}"
        else:
            ping_cmd = f"ping -c 1 -W 1 {ip}"
        
        try:
            # Executa o comando ping e verifica o código de retorno
            return subprocess.call(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True) == 0
        except:
            return False
    
    def get_mac_address(self, ip):
        """
        Obtém o endereço MAC de um dispositivo.
        
        Args:
            ip: Endereço IP do dispositivo
            
        Returns:
            str: Endereço MAC ou None se não for possível obter
        """
        if platform.system() == "Windows":
            try:
                # Usa o comando arp para obter o MAC
                output = subprocess.check_output(f"arp -a {ip}", shell=True).decode()
                for line in output.split('\n'):
                    if ip in line:
                        parts = line.split()
                        for part in parts:
                            if '-' in part or ':' in part:  # Formato de MAC address
                                return part
            except:
                pass
        return None
    
    def get_hostname(self, ip):
        """
        Resolve o nome de host a partir do IP.
        
        Args:
            ip: Endereço IP do dispositivo
            
        Returns:
            str: Nome do host ou None se não for possível resolver
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except:
            return None
    
    def scan_ports(self, ip, port_range=(1, 1024), callback=None):
        """
        Verifica portas abertas em um dispositivo.
        
        Args:
            ip: Endereço IP do dispositivo
            port_range: Tupla com intervalo de portas (início, fim)
            callback: Função de callback para atualizar a interface
            
        Returns:
            dict: Dicionário com as portas abertas e seus serviços
        """
        if ip not in self.scan_results:
            self.scan_results[ip] = {
                'mac': self.get_mac_address(ip),
                'hostname': self.get_hostname(ip),
                'ports': {},
                'status': 'unknown',
                'os': {'name': 'Desconhecido', 'confidence': 0}
            }
        
        open_ports = {}
        start_port, end_port = port_range
        
        print(f"Iniciando varredura de portas em {ip} (portas {start_port}-{end_port})")
        start_time = time.time()
        
        # Cria threads para verificar portas em paralelo
        q = Queue()
        threads = []
        num_threads = min(100, end_port - start_port + 1)
        
        # Função que será executada por cada thread
        def port_scanner_worker():
            while not self.stop_scan_flag:
                try:
                    port = q.get(block=False)
                except:
                    break
                
                try:
                    # Cria um socket e tenta conectar à porta
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    result = s.connect_ex((ip, port))
                    s.close()
                    
                    if result == 0:
                        # Porta aberta, tenta identificar o serviço
                        service = self.get_service_name(port)
                        open_ports[port] = service
                        
                        # Atualiza os resultados
                        self.scan_results[ip]['ports'][port] = service
                        self.scan_results[ip]['status'] = 'online'
                        
                        if callback:
                            callback(ip, port, service)
                except:
                    pass
                
                q.task_done()
        
        # Adiciona todas as portas à fila
        for port in range(start_port, end_port + 1):
            q.put(port)
        
        # Inicia as threads
        for _ in range(num_threads):
            t = threading.Thread(target=port_scanner_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Espera a conclusão da varredura
        q.join()
        
        # Se a varredura foi interrompida, limpa as threads
        if self.stop_scan_flag:
            for _ in range(num_threads):
                if not q.empty():
                    q.get()
                    q.task_done()
        
        end_time = time.time()
        print(f"Varredura de portas concluída em {end_time - start_time:.2f} segundos")
        print(f"Encontradas {len(open_ports)} portas abertas em {ip}")
        
        # Detecta o sistema operacional após a varredura de portas
        if self.os_detector and open_ports:
            print(f"Detectando sistema operacional de {ip}...")
            os_result = self.os_detector.detect_os(ip, open_ports)
            self.scan_results[ip]['os'] = {
                'name': os_result['os'],
                'confidence': os_result['confidence']
            }
            print(f"Sistema operacional detectado: {os_result['os']} (Confiança: {os_result['confidence']:.1f}%)")
        
        return open_ports
    
    def get_service_name(self, port):
        """
        Obtém o nome do serviço associado a uma porta.
        
        Args:
            port: Número da porta
            
        Returns:
            str: Nome do serviço ou "unknown"
        """
        try:
            return socket.getservbyport(port)
        except:
            # Serviços comuns que podem não estar no banco de dados
            common_ports = {
                21: "FTP",
                22: "SSH",
                23: "Telnet",
                25: "SMTP",
                53: "DNS",
                80: "HTTP",
                110: "POP3",
                115: "SFTP",
                135: "RPC",
                139: "NetBIOS",
                143: "IMAP",
                194: "IRC",
                443: "HTTPS",
                445: "SMB",
                1433: "MSSQL",
                3306: "MySQL",
                3389: "RDP",
                5900: "VNC",
                8080: "HTTP-Proxy"
            }
            return common_ports.get(port, "unknown")
    
    def stop_scan(self):
        """Interrompe qualquer varredura em andamento."""
        self.stop_scan_flag = True
        print("Solicitação de interrupção de varredura recebida")
    
    def get_scan_summary(self):
        """
        Gera um resumo da última varredura.
        
        Returns:
            dict: Resumo da varredura
        """
        total_devices = len(self.scan_results)
        total_open_ports = sum(len(device['ports']) for device in self.scan_results.values())
        
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'network': self.network,
            'local_ip': self.local_ip,
            'gateway': self.gateway,
            'total_devices': total_devices,
            'total_open_ports': total_open_ports,
            'devices': self.scan_results
        }


# Função para teste do módulo
if __name__ == "__main__":
    scanner = NetworkScanner()
    print(f"IP Local: {scanner.local_ip}")
    print(f"Gateway: {scanner.gateway}")
    print(f"Rede: {scanner.network}")
    
    # Callback de exemplo
    def update_callback(ip, data=None):
        if data:
            hostname = data.get('hostname', 'Desconhecido')
            print(f"Dispositivo encontrado: {ip} ({hostname})")
        else:
            print(f"Dispositivo encontrado: {ip}")
    
    # Executa uma varredura de teste
    print("\nIniciando varredura de rede...")
    results = scanner.scan_network_ping(update_callback)
    
    print("\nResultados da varredura:")
    for ip, data in results.items():
        hostname = data.get('hostname', 'Desconhecido')
        mac = data.get('mac', 'Desconhecido')
        print(f"IP: {ip}, Hostname: {hostname}, MAC: {mac}")
        
        # Verifica portas em alguns dispositivos (apenas para teste)
        if ip == scanner.local_ip or ip == scanner.gateway:
            print(f"  Verificando portas em {ip}...")
            ports = scanner.scan_ports(ip, (1, 100))
            for port, service in ports.items():
                print(f"  Porta {port}: {service}")
    
    print("\nResumo da varredura:")
    summary = scanner.get_scan_summary()
    print(f"Rede escaneada: {summary['network']}")
    print(f"Total de dispositivos: {summary['total_devices']}")
    print(f"Total de portas abertas: {summary['total_open_ports']}")
