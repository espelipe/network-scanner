## Atualização do Manual do Usuário - Novas Funcionalidades

### Mapa de Calor na Visualização de Rede

A visualização de rede agora inclui um mapa de calor que permite identificar rapidamente quais dispositivos têm mais serviços expostos na rede. O mapa de calor utiliza um gradiente de cores e tamanho para representar o número de portas abertas em cada dispositivo:

- **Cores**: Os dispositivos são coloridos em um gradiente que vai do azul (poucas portas abertas) ao vermelho (muitas portas abertas)
- **Tamanho**: Dispositivos com mais portas abertas são representados por círculos maiores
- **Contagem**: O número de portas abertas é exibido dentro de cada círculo

Esta visualização facilita a identificação imediata de dispositivos que podem requerer atenção especial do ponto de vista de segurança.

### Detecção de Sistema Operacional

O scanner agora é capaz de detectar o sistema operacional dos dispositivos na rede, utilizando múltiplas técnicas:

1. **Análise de TTL (Time To Live)**: Examina o valor TTL das respostas de ping para inferir o sistema operacional
2. **Padrões de Portas Abertas**: Identifica sistemas operacionais com base em combinações típicas de portas abertas
3. **Análise de Banners**: Examina banners de serviços para identificar informações sobre o sistema operacional

A detecção de sistema operacional é realizada automaticamente após a varredura de portas e os resultados são exibidos na interface com um nível de confiança associado.

### Como Usar as Novas Funcionalidades

1. **Mapa de Calor**:
   - Execute uma varredura de rede normalmente
   - Acesse a aba "Visualização" para ver o mapa de calor
   - Observe a legenda na parte inferior da visualização para interpretar as cores

2. **Detecção de Sistema Operacional**:
   - Execute uma varredura de rede
   - Selecione um dispositivo e execute uma varredura de portas
   - O sistema operacional detectado será exibido nas informações do dispositivo
   - Note que a precisão da detecção aumenta com o número de portas verificadas

### Sugestões de Melhorias Futuras

Foi criado um documento detalhado com sugestões para melhorias futuras do scanner de rede. Este documento está disponível no arquivo `feature_suggestions.md` e inclui recomendações para:

- Análise de vulnerabilidades
- Monitoramento contínuo
- Melhorias na interface e usabilidade
- Recursos avançados de segurança e análise
- Integrações com outras ferramentas

Recomendamos revisar estas sugestões para planejar o desenvolvimento futuro da ferramenta.
