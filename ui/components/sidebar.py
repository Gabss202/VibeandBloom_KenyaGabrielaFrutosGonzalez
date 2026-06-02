# ui/components/sidebar.py
import customtkinter as ctk
import ui.styles as st

class SidebarVibes(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Título principal de la app
        self.lbl_logo = ctk.CTkLabel(
            self, text="Novelia", font=(st.FONT_TITULO, 36, "bold"), text_color=st.ORO_PRIMARIO
        )
        self.lbl_logo.pack(anchor="w", pady=(20, 2))
        
        self.lbl_sub = ctk.CTkLabel(
            self, text="Libros que combinan\ncon tu vibe.", font=(st.FONT_CUERPO, 13),
            text_color=st.TEXT_MUTED, justify="left"
        )
        self.lbl_sub.pack(anchor="w", pady=(0, 30))
        
        # Sección de VIBES fijas
        self.lbl_seccion = ctk.CTkLabel(
            self, text="VIBES", font=(st.FONT_CUERPO, 12, "bold"), text_color=st.ORO_ACCENTO
        )
        self.lbl_seccion.pack(anchor="w", pady=(0, 10))
        
        # Lista de botones estéticos simulando el lateral
        vibes = [("🕯️ Cozy", "Relajante, hogareña"), 
                 ("🍁 Nostálgica", "Melancólica, emotiva"), 
                 ("💖 Romántica", "Dulce, intensa"), 
                 ("🧭 Aventurera", "Emocionante, libre"), 
                 ("🌙 Misteriosa", "Oscura, intrigante")]
                 
        for titulo, desc in vibes:
            btn = ctk.CTkButton(
                self, text=f"{titulo}\n{desc}", font=(st.FONT_CUERPO, 11),
                fg_color=st.BG_TARJETA, text_color=st.TEXT_CLARO,
                hover_color="#2A2420", height=45, corner_radius=10, anchor="w"
            )
            btn.pack(fill="x", pady=5)