# Manual do Usuário - Mini Ferramenta de Varredura de Rede Local

## Introdução

A Mini Ferramenta de Varredura de Rede Local é uma aplicação desenvolvida para Windows que permite descobrir dispositivos conectados à sua rede local, verificar portas abertas e visualizar a topologia da rede de forma gráfica.

## Requisitos do Sistema

- Sistema Operacional: Windows 7/8/10/11
- Python 3.6 ou superior (caso não esteja usando a versão empacotada)
- Bibliotecas Python (para versão não empacotada):
  - socket
  - scapy
  - tkinter
  - PIL (Pillow)
  - threading

## Instalação

### Versão Empacotada (Executável)

1. Extraia o arquivo ZIP em qualquer pasta do seu computador
2. Execute o arquivo `network_scanner.exe`

### Versão Python

1. Certifique-se de ter o Python 3.6 ou superior instalado
2. Instale as bibliotecas necessárias:
   ```
   pip install scapy pillow
   ```
3. Extraia os arquivos do projeto em uma pasta
4. Execute o arquivo `main.py`:
   ```
   python main.py
   ```

## Interface da Aplicação

A interface da aplicação é dividida em várias seções:

### Barra de Menu

- **Arquivo**: Opções para iniciar/parar varreduras, salvar e exportar resultados
- **Histórico**: Gerenciamento de varreduras anteriores
- **Ferramentas**: Configurações e visualização da rede
- **Ajuda**: Informações de ajuda e sobre a aplicação

### Painel de Informações da Rede

Exibe informações básicas sobre a rede local:
- IP Local
- Gateway
- Rede
- Status atual

### Controles de Varredura

- **Iniciar Varredura**: Inicia a descoberta de dispositivos na rede
- **Parar**: Interrompe uma varredura em andamento
- **Intervalo de Portas**: Define o intervalo de portas a serem verificadas

### Abas de Visualização

#### Aba Dispositivos

Exibe uma tabela com todos os dispositivos encontrados na rede, incluindo:
- Endereço IP
- Nome do Host
- Endereço MAC
- Status
- Portas Abertas

#### Aba Detalhes

Exibe informações detalhadas sobre o dispositivo selecionado:
- Informações básicas (IP, hostname, MAC, status)
- Lista de portas abertas com serviços identificados
- Botões para verificar portas e abrir no navegador

#### Aba Visualização

Exibe uma representação gráfica da rede com diferentes tipos de visualização:
- Radial: Dispositivos em círculo ao redor do gateway
- Hierárquica: Estrutura em árvore com o gateway no topo
- Força: Simulação de forças físicas entre os dispositivos

## Funcionalidades

### Descoberta de Dispositivos

1. Clique no botão "Iniciar Varredura"
2. A aplicação irá descobrir dispositivos conectados à rede local
3. Os dispositivos encontrados serão exibidos na tabela da aba "Dispositivos"
4. O gateway e o dispositivo local serão destacados com cores diferentes

### Verificação de Portas

1. Selecione um dispositivo na tabela
2. Defina o intervalo de portas a serem verificadas
3. Clique no botão "Verificar Portas"
4. As portas abertas serão exibidas na aba "Detalhes"

### Salvar e Exportar Resultados

1. Após uma varredura, acesse o menu "Arquivo"
2. Selecione "Salvar Resultados" para armazenar a varredura no histórico
3. Selecione "Exportar para CSV" ou "Exportar para TXT" para exportar os resultados

### Histórico de Varreduras

1. Acesse o menu "Histórico"
2. Selecione "Carregar Varredura Anterior" para visualizar resultados de varreduras passadas
3. Selecione "Gerenciar Histórico" para visualizar, carregar ou excluir varreduras salvas

### Visualização da Rede

1. Após uma varredura, acesse a aba "Visualização"
2. Selecione o tipo de visualização desejado no menu suspenso
3. Clique em "Atualizar Visualização" para atualizar a representação gráfica

## Menu de Contexto

Clique com o botão direito em um dispositivo na tabela para acessar o menu de contexto:
- **Verificar Portas**: Inicia a verificação de portas para o dispositivo selecionado
- **Copiar IP/MAC/Hostname**: Copia a informação para a área de transferência
- **Abrir no Navegador**: Tenta abrir o dispositivo no navegador (útil para servidores web)

## Configurações

Acesse o menu "Ferramentas" > "Configurações" para ajustar:
- Intervalo de portas padrão
- Timeout de varredura
- Tema da interface
- Tamanho da fonte
- Método de varredura
- Número de threads

## Dicas e Observações

- A varredura de rede pode levar algum tempo, dependendo do tamanho da rede
- A verificação de portas pode ser detectada por firewalls e sistemas de segurança
- Use esta ferramenta apenas em redes que você tem permissão para analisar
- O método de varredura ARP é mais rápido, mas requer a biblioteca scapy
- O método de varredura Ping é mais lento, mas funciona em qualquer sistema
- Dispositivos com firewall ativo podem não responder a pings ou verificações de porta

## Solução de Problemas

### A aplicação não inicia

- Verifique se o Python está instalado corretamente (versão não empacotada)
- Verifique se todas as bibliotecas necessárias estão instaladas
- Tente executar a aplicação como administrador

### Nenhum dispositivo é encontrado

- Verifique sua conexão de rede
- Verifique se o firewall não está bloqueando a aplicação
- Tente usar o método de varredura alternativo nas configurações

### Erro ao verificar portas

- Verifique se o dispositivo está online
- Verifique se o firewall não está bloqueando a verificação
- Tente um intervalo menor de portas

### Visualização da rede não aparece

- Certifique-se de ter realizado uma varredura primeiro
- Verifique se o canvas de visualização está visível
- Tente redimensionar a janela da aplicação

## Suporte

Se encontrar problemas ou tiver sugestões para melhorias, entre em contato através do e-mail: suporte@exemplo.com
