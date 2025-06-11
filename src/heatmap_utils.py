#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Utilidades para Mapa de Calor
--------------------------------------
Este módulo contém funções para criar e manipular mapas de calor para visualização de rede.
"""

import math
import colorsys
import tkinter as tk

def get_heat_color(value, min_value=0, max_value=10):
    """
    Gera uma cor para o mapa de calor baseado em um valor.
    
    Args:
        value: Valor a ser convertido em cor (ex: número de portas abertas)
        min_value: Valor mínimo esperado (padrão: 0)
        max_value: Valor máximo esperado (padrão: 10)
        
    Returns:
        str: Código de cor hexadecimal (#RRGGBB)
    """
    # Garante que o valor esteja dentro dos limites
    if value < min_value:
        value = min_value
    if value > max_value:
        value = max_value
    
    # Normaliza o valor para o intervalo [0, 1]
    if max_value == min_value:
        normalized = 0
    else:
        normalized = (value - min_value) / (max_value - min_value)
    
    # Gera cores do azul (frio) ao vermelho (quente)
    # Azul -> Ciano -> Verde -> Amarelo -> Laranja -> Vermelho
    if normalized < 0.2:
        # Azul para Ciano (aumenta o verde)
        r = 0
        g = int(255 * (normalized / 0.2))
        b = 255
    elif normalized < 0.4:
        # Ciano para Verde (diminui o azul)
        r = 0
        g = 255
        b = int(255 * (1 - (normalized - 0.2) / 0.2))
    elif normalized < 0.6:
        # Verde para Amarelo (aumenta o vermelho)
        r = int(255 * ((normalized - 0.4) / 0.2))
        g = 255
        b = 0
    elif normalized < 0.8:
        # Amarelo para Laranja (diminui o verde)
        r = 255
        g = int(255 * (1 - (normalized - 0.6) / 0.2))
        b = 0
    else:
        # Laranja para Vermelho (mantém vermelho)
        r = 255
        g = 0
        b = 0
    
    # Converte para hexadecimal
    return f"#{r:02x}{g:02x}{b:02x}"

def get_heat_alpha_color(value, min_value=0, max_value=10, base_color="#6495ED", alpha_min=0.2, alpha_max=1.0):
    """
    Gera uma cor com transparência para o mapa de calor baseado em um valor.
    Útil para sobrepor cores em visualizações existentes.
    
    Args:
        value: Valor a ser convertido em transparência (ex: número de portas abertas)
        min_value: Valor mínimo esperado (padrão: 0)
        max_value: Valor máximo esperado (padrão: 10)
        base_color: Cor base em formato hexadecimal (padrão: azul)
        alpha_min: Valor mínimo de alpha/opacidade (padrão: 0.2)
        alpha_max: Valor máximo de alpha/opacidade (padrão: 1.0)
        
    Returns:
        tuple: (cor_hex, alpha_value) - Código de cor hexadecimal e valor alpha
    """
    # Garante que o valor esteja dentro dos limites
    if value < min_value:
        value = min_value
    if value > max_value:
        value = max_value
    
    # Normaliza o valor para o intervalo [0, 1]
    if max_value == min_value:
        normalized = 0
    else:
        normalized = (value - min_value) / (max_value - min_value)
    
    # Calcula o valor alpha
    alpha = alpha_min + normalized * (alpha_max - alpha_min)
    
    return (base_color, alpha)

def get_heat_radius(value, min_value=0, max_value=10, min_radius=15, max_radius=30):
    """
    Calcula o raio de um círculo baseado em um valor para visualização de mapa de calor.
    
    Args:
        value: Valor a ser convertido em raio (ex: número de portas abertas)
        min_value: Valor mínimo esperado (padrão: 0)
        max_value: Valor máximo esperado (padrão: 10)
        min_radius: Raio mínimo (padrão: 15)
        max_radius: Raio máximo (padrão: 30)
        
    Returns:
        float: Valor do raio
    """
    # Garante que o valor esteja dentro dos limites
    if value < min_value:
        value = min_value
    if value > max_value:
        value = max_value
    
    # Normaliza o valor para o intervalo [0, 1]
    if max_value == min_value:
        normalized = 0
    else:
        normalized = (value - min_value) / (max_value - min_value)
    
    # Calcula o raio
    radius = min_radius + normalized * (max_radius - min_radius)
    
    return radius

def create_heatmap_legend(canvas, x, y, width, height, title="Intensidade (portas abertas)"):
    """
    Cria uma legenda para o mapa de calor no canvas.
    
    Args:
        canvas: Canvas Tkinter onde desenhar a legenda
        x, y: Coordenadas do canto superior esquerdo da legenda
        width, height: Largura e altura da legenda
        title: Título da legenda
        
    Returns:
        None
    """
    # Desenha o fundo da legenda
    canvas.create_rectangle(
        x, y,
        x + width, y + height,
        fill="#FFFFFF",
        outline="#000000",
        width=1,
        tags=("heatmap_legend")
    )
    
    # Desenha o título
    canvas.create_text(
        x + width // 2,
        y + 15,
        text=title,
        font=("Segoe UI", 9, "bold"),
        tags=("heatmap_legend")
    )
    
    # Desenha o gradiente
    gradient_width = width - 20
    gradient_height = 20
    gradient_x = x + 10
    gradient_y = y + 30
    
    # Número de segmentos no gradiente
    segments = 50
    segment_width = gradient_width / segments
    
    for i in range(segments):
        # Valor normalizado de 0 a 1
        normalized = i / (segments - 1)
        
        # Obtém a cor para este segmento
        if normalized < 0.2:
            # Azul para Ciano
            r = 0
            g = int(255 * (normalized / 0.2))
            b = 255
        elif normalized < 0.4:
            # Ciano para Verde
            r = 0
            g = 255
            b = int(255 * (1 - (normalized - 0.2) / 0.2))
        elif normalized < 0.6:
            # Verde para Amarelo
            r = int(255 * ((normalized - 0.4) / 0.2))
            g = 255
            b = 0
        elif normalized < 0.8:
            # Amarelo para Laranja
            r = 255
            g = int(255 * (1 - (normalized - 0.6) / 0.2))
            b = 0
        else:
            # Laranja para Vermelho
            r = 255
            g = 0
            b = 0
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Desenha o segmento
        canvas.create_rectangle(
            gradient_x + i * segment_width,
            gradient_y,
            gradient_x + (i + 1) * segment_width,
            gradient_y + gradient_height,
            fill=color,
            outline="",
            tags=("heatmap_legend")
        )
    
    # Desenha os rótulos
    canvas.create_text(
        gradient_x,
        gradient_y + gradient_height + 15,
        text="Baixo",
        font=("Segoe UI", 8),
        anchor=tk.W,
        tags=("heatmap_legend")
    )
    
    canvas.create_text(
        gradient_x + gradient_width,
        gradient_y + gradient_height + 15,
        text="Alto",
        font=("Segoe UI", 8),
        anchor=tk.E,
        tags=("heatmap_legend")
    )

# Teste do módulo
if __name__ == "__main__":
    import tkinter as tk
    
    # Cria uma janela de teste
    root = tk.Tk()
    root.title("Teste de Mapa de Calor")
    root.geometry("600x400")
    
    # Cria um canvas
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Testa as cores
    for i in range(11):
        color = get_heat_color(i, 0, 10)
        canvas.create_rectangle(
            50 + i * 40, 50,
            50 + (i + 1) * 40, 90,
            fill=color,
            outline="#000000"
        )
        canvas.create_text(
            50 + i * 40 + 20, 100,
            text=str(i),
            font=("Segoe UI", 10)
        )
    
    # Testa a legenda
    create_heatmap_legend(canvas, 50, 150, 400, 80)
    
    root.mainloop()
