# Arquitetura da Mini Ferramenta de Varredura de Rede Local

## Visão Geral
A ferramenta de varredura de rede local será desenvolvida com uma arquitetura modular que separa as responsabilidades em componentes distintos, facilitando a manutenção e extensão futura. A aplicação será desenvolvida para Windows utilizando Python com interface gráfica Tkinter.

## Componentes Principais

### 1. Módulo de Varredura de Rede (`network_scanner.py`)
Responsável por toda a lógica de descoberta de dispositivos e análise de portas.

**Funcionalidades:**
- Descoberta de IPs ativos na rede local
- Verificação de portas abertas em dispositivos específicos
- Resolução de nomes de dispositivos (quando disponível)
- Detecção do gateway e informações da rede local

**Dependências:**
- `socket`: Para comunicação de rede básica
- `scapy`: Para funcionalidades avançadas de varredura
- `subprocess`: Para executar comandos do sistema (como ping)

### 2. Módulo de Interface Gráfica (`gui.py`)
Gerencia toda a interface do usuário usando Tkinter.

**Componentes:**
- Janela principal com menu e barra de status
- Painel de controle para configurações de varredura
- Área de visualização de resultados (tabela)
- Visualização gráfica da rede (mapa de dispositivos)
- Diálogos para configurações e exportação

**Dependências:**
- `tkinter`: Para a interface gráfica
- `ttk`: Para widgets modernos
- `PIL/Pillow`: Para manipulação de imagens e ícones

### 3. Módulo de Gerenciamento de Dados (`data_manager.py`)
Gerencia o armazenamento, carregamento e exportação de resultados.

**Funcionalidades:**
- Salvar resultados de varredura em diferentes formatos (CSV, TXT)
- Carregar resultados de varreduras anteriores
- Manter histórico de varreduras
- Comparar resultados entre diferentes varreduras

**Dependências:**
- `csv`: Para manipulação de arquivos CSV
- `json`: Para armazenamento estruturado de dados
- `datetime`: Para registro de timestamps

### 4. Módulo Principal (`main.py`)
Ponto de entrada da aplicação, responsável por inicializar e coordenar os outros módulos.

**Responsabilidades:**
- Inicialização da aplicação
- Coordenação entre os módulos
- Gerenciamento de configurações globais
- Tratamento de erros de alto nível

## Fluxo de Dados

1. O usuário interage com a interface gráfica para iniciar uma varredura
2. A interface passa os parâmetros para o módulo de varredura
3. O módulo de varredura executa as operações de rede e retorna os resultados
4. Os resultados são exibidos na interface e podem ser salvos pelo módulo de gerenciamento de dados
5. O histórico de varreduras é mantido e pode ser consultado pelo usuário

## Estrutura de Arquivos

```
network_scanner/
│
├── main.py                  # Ponto de entrada da aplicação
├── network_scanner.py       # Módulo de varredura de rede
├── gui.py                   # Módulo de interface gráfica
├── data_manager.py          # Módulo de gerenciamento de dados
├── utils.py                 # Funções utilitárias
│
├── assets/                  # Recursos gráficos
│   ├── icons/               # Ícones da aplicação
│   └── images/              # Imagens utilizadas na interface
│
├── data/                    # Diretório para armazenamento de dados
│   └── history/             # Histórico de varreduras
│
└── docs/                    # Documentação
    └── user_manual.md       # Manual do usuário
```

## Considerações Técnicas

### Desempenho
- A varredura de rede será executada em threads separadas para não bloquear a interface
- Implementação de timeout para operações de rede para evitar bloqueios
- Opção para limitar o número de conexões simultâneas

### Segurança
- Validação de entrada do usuário para evitar injeção de comandos
- Limitação de frequência de varredura para evitar sobrecarga da rede
- Avisos sobre implicações legais de varredura de redes

### Extensibilidade
- Arquitetura modular permite adicionar novas funcionalidades
- Sistema de plugins pode ser implementado no futuro
- Configurações salvas em formato JSON para fácil modificação

## Funcionalidades Futuras Potenciais
- Varredura periódica automática
- Notificações de novos dispositivos
- Detecção de sistemas operacionais
- Integração com ferramentas de segurança
- Suporte a redes IPv6
