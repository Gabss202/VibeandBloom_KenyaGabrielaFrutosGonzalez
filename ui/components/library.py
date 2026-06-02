# ui/components/library.py
import customtkinter as ctk
import ui.styles as st

class LibraryPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Título del bloque derecho
        self.lbl_title = ctk.CTkLabel(self, text="Tu biblioteca", font=(st.FONT_TITULO, 18, "bold"), text_color=st.TEXT_CLARO)
        self.lbl_title.pack(anchor="w", pady=(10, 10))
        
        # Carpetas requeridas: Leyendo, Quiero Leer, Leídos
        folders = [(" Leyendo", "5 libros"), ("⭐ Quiero leer", "12 libros"), ("✓ Leídos", "23 libros")]
        for f_name, count in folders:
            card = ctk.CTkFrame(self, fg_color=st.BG_TARJETA, height=45, corner_radius=10)
            card.pack(fill="x", pady=4)
            card.pack_propagate(False)
            
            lbl = ctk.CTkLabel(card, text=f"{f_name}  ({count})", font=(st.FONT_CUERPO, 12), text_color=st.TEXT_CLARO, padx=15)
            lbl.pack(side="left", fill="y")

        # Sección de progreso gráfico simulado
        self.lbl_prog = ctk.CTkLabel(self, text="Progreso de lectura", font=(st.FONT_TITULO, 16, "bold"), text_color=st.TEXT_CLARO)
        self.lbl_prog.pack(anchor="w", pady=(25, 10))
        
        self.frame_chart = ctk.CTkFrame(self, fg_color=st.BG_TARJETA, height=120, corner_radius=12)
        self.frame_chart.pack(fill="x")
        self.frame_chart.pack_propagate(False)
        
        lbl_stats = ctk.CTkLabel(self.frame_chart, text="📊 Gráfica de Lectura Mensual\n(Módulos SQLite enlazados)", font=(st.FONT_CUERPO, 11, "italic"), text_color=st.TEXT_MUTED)
        lbl_stats.pack(expand=True)