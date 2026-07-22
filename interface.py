import webbrowser
import customtkinter as ctk
import tkintermapview
from tkinter import messagebox
import threading
import core
import animações
from sistema_logs import GerenciadorDeLogs

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class InterfaceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoLead Pro - AI Prospector")
        self.geometry("1000x650")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.dados_gerados = []
        self.janela_logs = None
        self.caixa_texto_logs = None
        self.raio_poligono = None 

        self.dados_gerados = []
        self.webhook_url = "" # <-- NOVA VARIÁVEL
        
        # Inicia o módulo de segurança importado
        self.seguranca = GerenciadorDeLogs()
        
        # Detecta quando o usuário clica no X para fechar e limpa tudo
        self.protocol("WM_DELETE_WINDOW", self.fechar_aplicativo)

        self.construir_design()

    def fechar_aplicativo(self):
        """Aciona o módulo de segurança para apagar logs e fecha a tela."""
        self.seguranca.encerrar_seguro()
        self.destroy()

    def construir_design(self):
        """Monta toda a interface visual com o Mapa."""
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="AutoLead Pro", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))

        ctk.CTkLabel(self.sidebar_frame, text="Sua Empresa:").grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.entry_empresa = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Ex: Distribuidora Silva")
        self.entry_empresa.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.sidebar_frame, text="Nicho Alvo:").grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        nichos_disponiveis = [
            "Salões de Beleza", "Varejistas", "Clínicas de Estética", 
            "Restaurantes", "Oficinas Mecânicas", "Academias", 
            "Imobiliárias", "Pet Shops"
        ]
        self.combo_busca = ctk.CTkComboBox(self.sidebar_frame, values=nichos_disponiveis, state="readonly")
        self.combo_busca.set("Varejistas") 
        self.combo_busca.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.label_raio = ctk.CTkLabel(self.sidebar_frame, text="Raio de Busca (5 km):")
        self.label_raio.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.slider_raio = ctk.CTkSlider(self.sidebar_frame, from_=1, to=50, number_of_steps=49, command=self.atualizar_raio_mapa)
        self.slider_raio.set(5)
        self.slider_raio.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        # --- CONFIGURAÇÃO DA CHAVE API ---
        ctk.CTkLabel(self.sidebar_frame, text="Chave API (Gemini):").grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        
        # O parâmetro show="*" esconde a chave como se fosse uma senha!
        self.entry_api = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Cole sua API Key aqui...", show="*")
        self.entry_api.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        
        # Criação do Link Clicável
        self.link_api = ctk.CTkLabel(self.sidebar_frame, text="🔗 Clique aqui para pegar sua chave", text_color="#00FFcc", cursor="hand2", font=ctk.CTkFont(size=12, underline=True))
        self.link_api.grid(row=9, column=0, padx=20, pady=(0, 10), sticky="w")
        self.link_api.bind("<Button-1>", lambda e: webbrowser.open("https://aistudio.google.com/app/apikey"))

        # --- SISTEMA HÍBRIDO DE MENSAGEM (IA vs MANUAL) ---
        self.modo_mensagem_var = ctk.StringVar(value="IA")
        
        self.switch_modo = ctk.CTkSwitch(
            self.sidebar_frame, 
            text="Modo: IA Gemini 🧠", 
            command=self.alternar_modo_mensagem,
            variable=self.modo_mensagem_var,
            onvalue="IA",
            offvalue="Manual"
        )
        # Atenção: O Switch agora foi para a linha (row) 10!
        self.switch_modo.grid(row=10, column=0, padx=20, pady=(15, 0), sticky="w")

        self.caixa_mensagem_manual = ctk.CTkTextbox(self.sidebar_frame, height=100)
        self.caixa_mensagem_manual.insert("1.0", "Olá, responsável pela {alvo}! Somos a {empresa} e temos uma proposta para vocês.")
        self.frame_acoes = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.frame_acoes.grid(row=12, column=0, padx=20, pady=20, sticky="ew")
        
        # Ajustamos as colunas para caber 3 botões
        self.frame_acoes.grid_columnconfigure(0, weight=3)
        self.frame_acoes.grid_columnconfigure(1, weight=1)
        self.frame_acoes.grid_columnconfigure(2, weight=0)

        self.btn_iniciar = ctk.CTkButton(self.frame_acoes, text="🚀 Iniciar", command=self.iniciar_thread)
        self.btn_iniciar.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_logs = ctk.CTkButton(self.frame_acoes, text="📜 Logs", fg_color="#444444", command=self.abrir_janela_logs)
        self.btn_logs.grid(row=0, column=1, padx=(5, 5), sticky="ew")
        
        # NOVO BOTÃO DE CONFIGURAÇÕES DE INTEGRAÇÃO
        self.btn_config = ctk.CTkButton(self.frame_acoes, text="⚙️", fg_color="#2B579A", width=40, command=self.abrir_janela_config)
        self.btn_config.grid(row=0, column=2, padx=(0, 0), sticky="ew")

# --- MAPA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.main_frame, text="Mapeamento de Prospecção Ao Vivo", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(15, 5))

        # CORREÇÃO: O database_path entra direto aqui na criação do widget!
        self.map_widget = tkintermapview.TkinterMapView(self.main_frame, corner_radius=10, database_path="mapa_cache_autolead.db")
        self.map_widget.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # 1. ATIVANDO O MODO ESCURO (Servidor CartoDB Dark Matter)
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png", max_zoom=19)
        
        # A linha "set_database_path" foi removida daqui.
        
        self.lat_atual, self.lng_atual = -19.9208, -43.9378
        self.map_widget.set_position(self.lat_atual, self.lng_atual) 
        self.map_widget.set_zoom(13)
        
        self.frame_botoes = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_botoes.grid(row=2, column=0, pady=10)
        
        self.btn_excel = ctk.CTkButton(self.frame_botoes, text="Baixar .XLSX", fg_color="#1D6F42", state="disabled", command=self.baixar_excel)
        self.btn_excel.pack(side="left", padx=10)
        
        self.btn_word = ctk.CTkButton(self.frame_botoes, text="Baixar .DOCX", fg_color="#2B579A", state="disabled", command=self.baixar_word)
        self.btn_word.pack(side="left", padx=10)

        self.atualizar_raio_mapa(self.slider_raio.get())

    def atualizar_raio_mapa(self, valor):
        raio_km = int(valor)
        self.label_raio.configure(text=f"Raio de Busca ({raio_km} km):")
        if self.raio_poligono is not None:
            self.map_widget.delete(self.raio_poligono)
        self.map_widget.set_position(self.lat_atual, self.lng_atual)

    def alternar_modo_mensagem(self):
        if self.modo_mensagem_var.get() == "Manual":
                self.switch_modo.configure(text="Modo: Texto Fixo ✍️")
                # Aqui estava row=8, mude para row=11
                self.caixa_mensagem_manual.grid(row=11, column=0, padx=20, pady=(10, 0), sticky="ew")
        else:
                self.switch_modo.configure(text="Modo: IA Gemini 🧠")
                self.caixa_mensagem_manual.grid_forget()

    def abrir_janela_logs(self):
        if self.janela_logs is None or not self.janela_logs.winfo_exists():
            self.janela_logs = ctk.CTkToplevel(self)
            self.janela_logs.title("Logs do Sistema")
            self.janela_logs.geometry("500x400")
            self.janela_logs.attributes("-topmost", True)
            
            self.caixa_texto_logs = ctk.CTkTextbox(self.janela_logs, font=("Consolas", 13), text_color="#00FFcc", fg_color="#1a1a1a")
            self.caixa_texto_logs.pack(padx=10, pady=10, fill="both", expand=True)
            self.caixa_texto_logs.insert("end", "--- Janela de Logs Iniciada ---\n")
        else:
            self.janela_logs.focus()

    def abrir_janela_config(self):
        """Abre o painel para conectar o AutoLead a robôs de disparo."""
        janela_config = ctk.CTkToplevel(self)
        janela_config.title("Integração Webhook")
        janela_config.geometry("500x250")
        janela_config.attributes("-topmost", True)
        
        ctk.CTkLabel(janela_config, text="Conecte seu Robô Externo (Make, Typebot, etc)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(janela_config, text="URL do Webhook (POST):").pack(anchor="w", padx=20)
        
        entrada_webhook = ctk.CTkEntry(janela_config, placeholder_text="https://seu-dominio.com/webhook/...", width=400)
        entrada_webhook.pack(pady=5, padx=20)
        
        # Se o usuário já tiver colado uma URL antes, ela continua preenchida
        if self.webhook_url:
            entrada_webhook.insert(0, self.webhook_url)
            
        def salvar_webhook():
            self.webhook_url = entrada_webhook.get().strip()
            if self.webhook_url:
                self.log(f"🔗 Webhook ativado: O AutoLead enviará dados para o seu robô!")
            else:
                self.log("🔗 Webhook desativado: Os disparos não serão automatizados.")
            janela_config.destroy()
            
        ctk.CTkButton(janela_config, text="Salvar Integração", command=salvar_webhook, fg_color="#2B579A").pack(pady=20)

    def log(self, texto):
        if self.caixa_texto_logs is not None and self.janela_logs is not None and self.janela_logs.winfo_exists():
            animações.escrever_log_animado(self.caixa_texto_logs, self, texto)
        self.seguranca.registrar(texto)

    def iniciar_thread(self):
        self.btn_iniciar.configure(state="disabled")
        if self.caixa_texto_logs is not None and self.janela_logs is not None and self.janela_logs.winfo_exists():
            self.caixa_texto_logs.delete("1.0", "end")
        threading.Thread(target=self.processamento).start()

    def processamento(self):
        empresa = self.entry_empresa.get()
        termo = self.combo_busca.get() 
        raio = int(self.slider_raio.get())

        if not empresa:
            self.log("❌ Erro: Preencha o nome da sua empresa!")
            self.btn_iniciar.configure(state="normal")
            return

        self.seguranca.registrar(f"--- NOVA BUSCA INICIADA ---")
        self.log(f"📍 Detectando sua localização...")
        
        lat_temp, lng_temp, cidade = core.obter_localizacao_atual()
        if lat_temp and lat_temp != -1:
            self.lat_atual = lat_temp
            self.lng_atual = lng_temp
            self.map_widget.set_position(self.lat_atual, self.lng_atual)
        
        self.log(f"✅ Foco travado em: {cidade}")
        self.log(f"📡 Varrendo um raio de {raio}km por '{termo}'...")

        self.dados_gerados = core.buscar_empresas_google(termo, self.lat_atual, self.lng_atual, raio)

        if not self.dados_gerados:
            self.log("⚠️ Nenhum alvo encontrado.")
            self.btn_iniciar.configure(state="normal")
            return

        self.map_widget.delete_all_marker()
        
        for emp in self.dados_gerados:
            self.log(f"\n🏢 Encontrado: {emp['Nome']}")
            if 'lat' in emp and 'lon' in emp:
                self.map_widget.set_marker(emp['lat'], emp['lon'], text=emp['Nome'])
                
            # VERIFICA QUAL MODO O USUÁRIO ESCOLHEU
            if self.modo_mensagem_var.get() == "IA":
                chave_api = self.entry_api.get() # Puxa a chave da interface
                self.log(f"🧠 IA formulando abordagem comercial...")
                emp['Mensagem Pronta'] = core.gerar_mensagem(emp['Nome'], empresa, chave_api)
            else:
                self.log(f"✍️ Aplicando seu Roteiro Fixo...")
                texto_base = self.caixa_mensagem_manual.get("1.0", "end-1c")
                
                # Bônus: Substitui as tags pelo nome real da empresa e do alvo
                texto_formatado = texto_base.replace("{empresa}", empresa).replace("{alvo}", emp['Nome'])
                emp['Mensagem Pronta'] = texto_formatado
                
            self.log(f"✅ Abordagem blindada criada!")

            # NOVA ETAPA: DISPARO DO WEBHOOK PARA O ROBÔ
            if self.webhook_url:
                self.log(f"🔗 Enviando {emp['Nome']} para o Robô Externo...")
                sucesso, msg_retorno = core.disparar_webhook(self.webhook_url, emp)
                if sucesso:
                    self.log(f"🟢 Sucesso: O robô assumiu a conversa!")
                else:
                    self.log(f"🔴 Erro Webhook: {msg_retorno}")

        self.log("\n🎉 Prospecção Finalizada!")
        
        self.btn_excel.configure(state="normal")
        self.btn_word.configure(state="normal")
        self.btn_iniciar.configure(state="normal")

    def baixar_excel(self):
        core.exportar_excel(self.dados_gerados)
        self.seguranca.registrar("Usuário baixou arquivo .XLSX")
        messagebox.showinfo("Sucesso", "Planilha salva!")

    def baixar_word(self):
        core.exportar_word(self.dados_gerados)
        self.seguranca.registrar("Usuário baixou arquivo .DOCX")
        messagebox.showinfo("Sucesso", "Documento salvo!")