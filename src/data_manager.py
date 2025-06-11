#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Gerenciamento de Dados
-------------------------------
Este módulo contém as funcionalidades para salvar, carregar e gerenciar
os resultados das varreduras de rede.
"""

import os
import csv
import json
import datetime
import shutil

class DataManager:
    """Classe para gerenciamento de dados da aplicação."""
    
    def __init__(self, base_dir="data"):
        """
        Inicializa o gerenciador de dados.
        
        Args:
            base_dir: Diretório base para armazenamento de dados
        """
        self.base_dir = base_dir
        self.history_dir = os.path.join(base_dir, "history")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Garante que os diretórios necessários existam."""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
    
    def save_scan_results(self, scan_data, filename=None):
        """
        Salva os resultados de uma varredura em formato JSON.
        
        Args:
            scan_data: Dados da varredura a serem salvos
            filename: Nome do arquivo (opcional)
            
        Returns:
            str: Caminho do arquivo salvo
        """
        if filename is None:
            # Gera um nome de arquivo baseado na data e hora
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_{timestamp}.json"
        
        filepath = os.path.join(self.history_dir, filename)
        
        # Adiciona timestamp se não existir
        if 'timestamp' not in scan_data:
            scan_data['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(scan_data, f, indent=2)
        
        print(f"Resultados salvos em {filepath}")
        return filepath
    
    def load_scan_results(self, filename):
        """
        Carrega resultados de uma varredura a partir de um arquivo JSON.
        
        Args:
            filename: Nome do arquivo a ser carregado
            
        Returns:
            dict: Dados da varredura ou None se o arquivo não existir
        """
        filepath = os.path.join(self.history_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Arquivo não encontrado: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Erro ao carregar arquivo {filepath}: {e}")
            return None
    
    def get_scan_history(self):
        """
        Obtém a lista de varreduras salvas.
        
        Returns:
            list: Lista de dicionários com informações sobre as varreduras
        """
        history = []
        
        if not os.path.exists(self.history_dir):
            return history
        
        for filename in os.listdir(self.history_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.history_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extrai informações básicas
                    info = {
                        'filename': filename,
                        'timestamp': data.get('timestamp', 'Desconhecido'),
                        'network': data.get('network', 'Desconhecido'),
                        'total_devices': data.get('total_devices', 0),
                        'total_open_ports': data.get('total_open_ports', 0)
                    }
                    history.append(info)
                except Exception as e:
                    print(f"Erro ao processar arquivo {filename}: {e}")
        
        # Ordena por timestamp (mais recente primeiro)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return history
    
    def export_to_csv(self, scan_data, filepath):
        """
        Exporta os resultados da varredura para um arquivo CSV.
        
        Args:
            scan_data: Dados da varredura
            filepath: Caminho completo do arquivo CSV
            
        Returns:
            bool: True se a exportação for bem-sucedida, False caso contrário
        """
        try:
            devices = scan_data.get('devices', {})
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Escreve o cabeçalho
                writer.writerow(['IP', 'Hostname', 'MAC', 'Status', 'Portas Abertas'])
                
                # Escreve os dados de cada dispositivo
                for ip, device in devices.items():
                    hostname = device.get('hostname', 'Desconhecido')
                    mac = device.get('mac', 'Desconhecido')
                    status = device.get('status', 'Desconhecido')
                    
                    # Formata as portas abertas
                    ports = device.get('ports', {})
                    ports_str = ', '.join([f"{port} ({service})" for port, service in ports.items()])
                    
                    writer.writerow([ip, hostname, mac, status, ports_str])
            
            print(f"Dados exportados para CSV: {filepath}")
            return True
        
        except Exception as e:
            print(f"Erro ao exportar para CSV: {e}")
            return False
    
    def export_to_txt(self, scan_data, filepath):
        """
        Exporta os resultados da varredura para um arquivo de texto.
        
        Args:
            scan_data: Dados da varredura
            filepath: Caminho completo do arquivo de texto
            
        Returns:
            bool: True se a exportação for bem-sucedida, False caso contrário
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Escreve o cabeçalho
                f.write("=== RELATÓRIO DE VARREDURA DE REDE ===\n\n")
                f.write(f"Data/Hora: {scan_data.get('timestamp', 'Desconhecido')}\n")
                f.write(f"Rede: {scan_data.get('network', 'Desconhecido')}\n")
                f.write(f"IP Local: {scan_data.get('local_ip', 'Desconhecido')}\n")
                f.write(f"Gateway: {scan_data.get('gateway', 'Desconhecido')}\n")
                f.write(f"Total de Dispositivos: {scan_data.get('total_devices', 0)}\n")
                f.write(f"Total de Portas Abertas: {scan_data.get('total_open_ports', 0)}\n\n")
                
                # Escreve os detalhes de cada dispositivo
                f.write("--- DISPOSITIVOS ENCONTRADOS ---\n\n")
                
                devices = scan_data.get('devices', {})
                for ip, device in devices.items():
                    hostname = device.get('hostname', 'Desconhecido')
                    mac = device.get('mac', 'Desconhecido')
                    status = device.get('status', 'Desconhecido')
                    
                    f.write(f"IP: {ip}\n")
                    f.write(f"Hostname: {hostname}\n")
                    f.write(f"MAC: {mac}\n")
                    f.write(f"Status: {status}\n")
                    
                    # Lista as portas abertas
                    ports = device.get('ports', {})
                    if ports:
                        f.write("Portas Abertas:\n")
                        for port, service in ports.items():
                            f.write(f"  - {port}: {service}\n")
                    else:
                        f.write("Portas Abertas: Nenhuma\n")
                    
                    f.write("\n")
            
            print(f"Dados exportados para TXT: {filepath}")
            return True
        
        except Exception as e:
            print(f"Erro ao exportar para TXT: {e}")
            return False
    
    def delete_scan_result(self, filename):
        """
        Remove um arquivo de resultado de varredura.
        
        Args:
            filename: Nome do arquivo a ser removido
            
        Returns:
            bool: True se a remoção for bem-sucedida, False caso contrário
        """
        filepath = os.path.join(self.history_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Arquivo não encontrado: {filepath}")
            return False
        
        try:
            os.remove(filepath)
            print(f"Arquivo removido: {filepath}")
            return True
        except Exception as e:
            print(f"Erro ao remover arquivo {filepath}: {e}")
            return False
    
    def clear_history(self):
        """
        Remove todos os arquivos de histórico.
        
        Returns:
            bool: True se a operação for bem-sucedida, False caso contrário
        """
        try:
            if os.path.exists(self.history_dir):
                shutil.rmtree(self.history_dir)
                os.makedirs(self.history_dir)
                print("Histórico de varreduras limpo com sucesso")
                return True
            return False
        except Exception as e:
            print(f"Erro ao limpar histórico: {e}")
            return False


# Função para teste do módulo
if __name__ == "__main__":
    # Dados de exemplo para teste
    sample_data = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'network': '192.168.1.0/24',
        'local_ip': '192.168.1.100',
        'gateway': '192.168.1.1',
        'total_devices': 3,
        'total_open_ports': 5,
        'devices': {
            '192.168.1.1': {
                'hostname': 'router.local',
                'mac': '00:11:22:33:44:55',
                'status': 'online',
                'ports': {
                    '80': 'http',
                    '443': 'https'
                }
            },
            '192.168.1.100': {
                'hostname': 'my-computer.local',
                'mac': 'AA:BB:CC:DD:EE:FF',
                'status': 'online',
                'ports': {
                    '22': 'ssh',
                    '3389': 'rdp'
                }
            },
            '192.168.1.101': {
                'hostname': 'another-device.local',
                'mac': '11:22:33:44:55:66',
                'status': 'online',
                'ports': {
                    '8080': 'http-proxy'
                }
            }
        }
    }
    
    # Cria uma instância do gerenciador de dados
    data_manager = DataManager()
    
    # Testa o salvamento de dados
    print("Testando salvamento de dados...")
    filepath = data_manager.save_scan_results(sample_data)
    
    # Testa a exportação para CSV
    print("\nTestando exportação para CSV...")
    csv_path = os.path.join(data_manager.base_dir, "export_test.csv")
    data_manager.export_to_csv(sample_data, csv_path)
    
    # Testa a exportação para TXT
    print("\nTestando exportação para TXT...")
    txt_path = os.path.join(data_manager.base_dir, "export_test.txt")
    data_manager.export_to_txt(sample_data, txt_path)
    
    # Testa a obtenção do histórico
    print("\nTestando obtenção do histórico...")
    history = data_manager.get_scan_history()
    for item in history:
        print(f"Arquivo: {item['filename']}, Data: {item['timestamp']}, Dispositivos: {item['total_devices']}")
    
    # Testa o carregamento de dados
    print("\nTestando carregamento de dados...")
    filename = os.path.basename(filepath)
    loaded_data = data_manager.load_scan_results(filename)
    if loaded_data:
        print(f"Dados carregados com sucesso: {loaded_data['timestamp']}")
    
    # Não remove os arquivos de teste para permitir inspeção manual
    print("\nTestes concluídos. Os arquivos de teste foram mantidos para inspeção.")
