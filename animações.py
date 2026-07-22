# animacoes.py
def escrever_log_animado(widget_texto, janela, texto):
    """
    Insere o log diretamente de forma segura para não travar a Interface Gráfica.
    """
    widget_texto.insert("end", texto + "\n")
    widget_texto.see("end") # Rola a tela para baixo automaticamente