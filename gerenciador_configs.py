# gerenciador_configs.py
import os
import json
from cryptography.fernet import Fernet

class GerenciadorConfigs:
    def __init__(self):
        caminho_appdata = os.environ.get('LOCALAPPDATA')
        
        self.pasta_projeto = os.path.join(caminho_appdata, "AutoLeadPro")
        os.makedirs(self.pasta_projeto, exist_ok=True)

        self.arquivo_chave = os.path.join(self.pasta_projeto, "mestra.key")
        self.arquivo_config = os.path.join(self.pasta_projeto, "config_segura.enc")
        
        self.chave = self.carregar_ou_criar_chave()
        self.fernet = Fernet(self.chave)

    def carregar_ou_criar_chave(self):
        """Cria uma chave de criptografia única na primeira vez e a oculta no Windows."""
        if not os.path.exists(self.arquivo_chave):
            chave = Fernet.generate_key()
            with open(self.arquivo_chave, "wb") as f:
                f.write(chave)
            
            try:
                # +h oculta o arquivo, +s diz que é um arquivo crítico do sistema
                os.system(f"attrib +h +s {self.arquivo_chave}")
            except:
                pass
                
            return chave
        else:
            with open(self.arquivo_chave, "rb") as f:
                return f.read()

    def salvar_configs(self, api_key, webhook_url):
        """Pega os dados puros, transforma em JSON e criptografa antes de salvar."""
        dados = {
            "api_key": api_key,
            "webhook_url": webhook_url
        }
        dados_json = json.dumps(dados)
        
        # Embaralha os dados
        dados_criptografados = self.fernet.encrypt(dados_json.encode())
        
        with open(self.arquivo_config, "wb") as f:
            f.write(dados_criptografados)

    def carregar_configs(self):
        """Lê o arquivo embaralhado, descriptografa e devolve os dados puros para o App."""
        if not os.path.exists(self.arquivo_config):
            return {"api_key": "", "webhook_url": ""}
        
        try:
            with open(self.arquivo_config, "rb") as f:
                dados_criptografados = f.read()
                
            # Desembaralha os dados
            dados_json = self.fernet.decrypt(dados_criptografados).decode()
            return json.loads(dados_json)
        except Exception as e:
            print(f"Erro ao descriptografar: {e}")
            return {"api_key": "", "webhook_url": ""}