# sistema_logs.py
import os
import shutil
from datetime import datetime

class GerenciadorDeLogs:
    def __init__(self, pasta_base="Logs_Sessao_AutoLead"):
        self.pasta_logs = pasta_base
        self.arquivo_log = None
        self.iniciar_sistema()

    def iniciar_sistema(self):
        """Cria uma pasta temporária para armazenar os logs da sessão atual."""
        if not os.path.exists(self.pasta_logs):
            os.makedirs(self.pasta_logs)
        
        agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.arquivo_log = os.path.join(self.pasta_logs, f"execucao_{agora}.txt")
        self.registrar("Sessão de Segurança iniciada. Todos os dados serão apagados ao fechar.")

    def registrar(self, mensagem):
        """Escreve as ações do usuário no arquivo .txt."""
        try:
            with open(self.arquivo_log, "a", encoding="utf-8") as f:
                hora = datetime.now().strftime("%H:%M:%S")
                f.write(f"[{hora}] {mensagem}\n")
        except:
            pass # Ignora erros menores para não travar o app principal

    def encerrar_seguro(self):
        """Apaga a pasta de logs inteira (Blindagem de Privacidade)."""
        try:
            if os.path.exists(self.pasta_logs):
                shutil.rmtree(self.pasta_logs)
        except Exception as e:
            print(f"Erro ao limpar arquivos temporários: {e}")