# Solução de Problemas - Visualizações Avançadas

Este documento contém soluções para problemas comuns que podem ocorrer ao utilizar as visualizações avançadas (3D e geoespacial) do Network Scanner.

## Problemas de Importação

Se você encontrar erros como `name 'Network3DVisualizer' is not defined` ou `name 'tk' is not defined`:

1. **Verifique se todos os arquivos estão no mesmo diretório**:
   - network_3d_visualizer.py
   - geospatial_visualizer.py
   - advanced_visualization.py
   - heatmap_utils.py

2. **Instale as dependências necessárias**:
   ```
   pip install plotly networkx folium requests
   ```

3. **Reinicie a aplicação** após instalar as dependências.

## Problemas com Visualização 3D

Se a visualização 3D não abrir ou apresentar erros:

1. **Verifique seu navegador padrão**:
   - A visualização 3D é aberta no navegador padrão do sistema
   - Certifique-se de que o navegador suporta JavaScript e WebGL

2. **Verifique a conexão de rede**:
   - Algumas bibliotecas podem precisar baixar recursos da internet

3. **Erro "basic_grid is not defined"**:
   - Este erro foi corrigido na versão atual
   - Se persistir, atualize para a versão mais recente

## Problemas com Visualização Geoespacial

Se a visualização geoespacial não funcionar corretamente:

1. **Verifique sua conexão com a internet**:
   - A visualização geoespacial requer acesso à internet para carregar mapas
   - Verifique se seu firewall não está bloqueando o acesso

2. **Problemas com geolocalização**:
   - Dispositivos em redes locais (IPs privados) são mostrados próximos à sua localização
   - A precisão da geolocalização depende dos dados disponíveis para cada IP

3. **Mapa não carrega**:
   - Tente novamente mais tarde, pois os serviços de geolocalização podem ter limitações de uso
   - Verifique se o arquivo HTML temporário foi criado corretamente

## Problemas de Interface

Se a interface apresentar problemas ao exibir detalhes do dispositivo:

1. **Erro ao exibir informações do sistema operacional**:
   - Este erro foi corrigido na versão atual
   - A detecção de SO agora é exibida corretamente na tabela e nos detalhes

2. **Problemas com o mapa de calor**:
   - Verifique se o arquivo heatmap_utils.py está presente e atualizado
   - O erro de importação do tkinter foi corrigido na versão atual

## Problemas de Desempenho

Se as visualizações estiverem lentas:

1. **Visualização 3D**:
   - Reduza o número de dispositivos na rede antes da varredura
   - Utilize um computador com melhores recursos gráficos

2. **Visualização Geoespacial**:
   - Desative o agrupamento de marcadores se houver muitos dispositivos
   - Reduza o zoom do mapa para melhorar o desempenho

## Contato para Suporte

Se você continuar enfrentando problemas após tentar estas soluções, entre em contato com o suporte técnico fornecendo:

1. Versão do sistema operacional
2. Versão do Python
3. Mensagem de erro completa
4. Descrição detalhada do problema
