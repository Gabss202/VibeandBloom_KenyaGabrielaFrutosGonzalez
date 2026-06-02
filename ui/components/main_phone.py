# ui/components/main_phone.py
import customtkinter as ctk
import ui.styles as st

class MainPhoneDisplay(ctk.CTkFrame):
    def __init__(self, master, on_search_callback, **kwargs):
        super().__init__(master, fg_color=st.BG_PRINCIPAL, border_color=st.BG_TARJETA, border_width=2, corner_radius=30, **kwargs)
        self.on_search = on_search_callback

        # Contenedor interno tipo pantalla de smartphone
        self.pack_propagate(False)
        
        # Saludo inicial
        self.lbl_user = ctk.CTkLabel(self, text="Hola, Usuario ✨", font=(st.FONT_CUERPO, 18, "bold"), text_color=st.TEXT_CLARO)
        self.lbl_user.pack(anchor="w", padx=20, pady=(25, 2))
        
        self.lbl_ask = ctk.CTkLabel(self, text="¿Qué vibe buscas hoy?", font=(st.FONT_CUERPO, 13), text_color=st.TEXT_MUTED)
        self.lbl_ask.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Barra de Entrada integrada
        self.entry_vibe = ctk.CTkEntry(
            self, placeholder_text="Inserta frase, canción o link...",
            fg_color=st.BG_TARJETA, border_color=st.ORO_ACCENTO, text_color=st.TEXT_CLARO,
            font=(st.FONT_CUERPO, 12), height=40, corner_radius=12
        )
        self.entry_vibe.pack(fill="x", padx=20, pady=5)
        
        # Botón de activación
        self.btn_go = ctk.CTkButton(
            self, text="Consultar al Oráculo 🔮", font=(st.FONT_CUERPO, 12, "bold"),
            fg_color=st.ORO_PRIMARIO, text_color=st.BG_PRINCIPAL, hover_color="#B39359",
            height=35, corner_radius=10, command=self.trigger_search
        )
        self.btn_go.pack(fill="x", padx=20, pady=(5, 15))

        # Panel de Recomendación Central
        self.scroll_phone = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_phone.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Espacio vacío para rellenar dinámicamente con los Agentes
        self.lbl_empty = ctk.CTkLabel(self.scroll_phone, text="Bloom está esperando tu mood...", font=(st.FONT_CUERPO, 11, "italic"), text_color=st.TEXT_MUTED)
        self.lbl_empty.pack(pady=60)

    def trigger_search(self):
        text = self.entry_vibe.get()
        if text.strip():
            self.on_search(text, self.scroll_phone)