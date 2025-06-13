# Network Scanner com Visualizações 3D e Geoespacial

![Status do Projeto](https://img.shields.io/badge/status-ativo-brightgreen)
![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Licença](https://img.shields.io/badge/licença-MIT-green)

Uma ferramenta avançada de escaneamento de rede com visualizações interativas em 3D e geoespacial, desenvolvida em Python. Esta aplicação permite detectar dispositivos em uma rede local, identificar sistemas operacionais, escanear portas abertas e visualizar a topologia da rede de formas inovadoras.

## 🚀 Funcionalidades

- **Escaneamento de Rede**: Detecta automaticamente todos os dispositivos em uma rede local
- **Detecção de Sistema Operacional**: Identifica o SO dos dispositivos conectados
- **Escaneamento de Portas**: Verifica portas abertas e serviços em execução
- **Mapa de Calor**: Visualização baseada na quantidade de portas abertas
- **Visualização 3D**: Representação tridimensional interativa da topologia da rede
- **Visualização Geoespacial**: Mapeamento geográfico dos dispositivos com IPs públicos
- **Interface Gráfica Intuitiva**: Fácil de usar, com informações detalhadas sobre cada dispositivo

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Bibliotecas listadas em `requirements.txt`

## 🔧 Instalação

1. Clone este repositório:
```bash
git clone https://github.com/espelipe/network-scanner.git
cd network-scanner
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python main.py
```

## 📊 Visualizações

### Visualização 3D
A visualização 3D permite explorar a topologia da rede em um ambiente tridimensional interativo, oferecendo uma nova perspectiva sobre as conexões entre dispositivos.

### Visualização Geoespacial
A visualização geoespacial mostra a distribuição geográfica dos dispositivos em um mapa interativo, permitindo identificar a localização física aproximada de cada dispositivo.

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal
- **Tkinter**: Interface gráfica base
- **Plotly**: Visualizações 3D interativas
- **Folium**: Mapas geoespaciais
- **NetworkX**: Modelagem de grafos de rede

## 📚 Documentação

- [Manual do Usuário](docs/user_manual.md)
- [Manual de Visualizações Avançadas](docs/advanced_visualization_manual.md)
- [Solução de Problemas](docs/troubleshooting.md)

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
