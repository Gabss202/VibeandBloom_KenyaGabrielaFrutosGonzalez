# ui/app.py
import customtkinter as ctk
import ui.styles as st
from ui.components.sidebar import SidebarVibes
from ui.components.main_phone import MainPhoneDisplay
from ui.components.library import LibraryPanel

# Importamos tu Agente 2
from agents.agent2_recommender import recomendar_libros_por_vibe

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tus imports normales van aquí abajo...
import customtkinter as ctk
import ui.styles as st
from ui.components.sidebar import SidebarVibes

class NoveliaDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Novelia — Luxury Dashboard")
        self.geometry("1100x720")
        self.configure(fg_color=st.BG_PRINCIPAL)
        
        # Forzar un grid layout de 3 columnas bien organizadas
        self.grid_columnconfigure(0, weight=1, minsize=220) # Sidebar
        self.grid_columnconfigure(1, weight=2, minsize=400) # Celular central
        self.grid_columnconfigure(2, weight=1, minsize=250) # Biblioteca
        self.grid_rowconfigure(0, weight=1)
        
        # Instanciar cada bloque pasándole su columna correspondiente
        self.sidebar = SidebarVibes(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=25, pady=20)
        
        self.phone = MainPhoneDisplay(self, on_search_callback=self.ejecutar_agentes_ui)
        self.phone.grid(row=0, column=1, sticky="nsew", padx=15, pady=25)
        
        self.library = LibraryPanel(self)
        self.library.grid(row=0, column=2, sticky="nsew", padx=25, pady=20)

    def ejecutar_agentes_ui(self, texto_vibe, contenedor_scroll):
        # Limpiar mensajes previos en el scroll del celular
        for w in contenedor_scroll.winfo_children():
            w.destroy()
            
        lbl_loading = ctk.CTkLabel(contenedor_scroll, text="🔮 Consultando capas de agentes...", font=(st.FONT_CUERPO, 12, "italic"), text_color=st.ORO_PRIMARIO)
        lbl_loading.pack(pady=30)
        self.update()
        
        # Llamar a tu lógica real del Agente 2
        resultado = recomendar_libros_por_vibe(texto_vibe)
        lbl_loading.destroy()
        
        # Pintar la recomendación destacada estilo tarjeta premium
        card_reco = ctk.CTkFrame(contenedor_scroll, fg_color=st.BG_TARJETA, corner_radius=15)
        card_reco.pack(fill="x", pady=10, padx=5)
        
        lbl_rec_title = ctk.CTkLabel(card_reco, text="Recomendación para ti", font=(st.FONT_CUERPO, 12, "bold"), text_color=st.ORO_PRIMARIO, padx=15, pady=10)
        lbl_rec_title.pack(anchor="w")
        
        for libro in resultado.get("libros", []):
            lbl_l = ctk.CTkLabel(card_reco, text=f"🌟 {libro}", font=(st.FONT_CUERPO, 12), text_color=st.TEXT_CLARO, padx=20, pady=4, justify="left", anchor="w")
            lbl_l.pack(fill="x")
            
        # Cuadro de Explicabilidad (Agente 3 / Crítico de Bloom)
        lbl_exp_t = ctk.CTkLabel(contenedor_scroll, text="¿Por qué este libro?", font=(st.FONT_CUERPO, 13, "bold"), text_color=st.ORO_PRIMARIO, pady=5)
        lbl_exp_t.pack(anchor="w", padx=5)
        
        lbl_exp = ctk.CTkLabel(contenedor_scroll, text=resultado.get("explicacion_bloom", ""), font=(st.FONT_CUERPO, 11), text_color=st.TEXT_CLARO, wraplength=320, justify="left", padx=5)
        lbl_exp.pack(fill="x", pady=5)

if __name__ == "__main__":
    app = NoveliaDashboard()
    app.mainloop()