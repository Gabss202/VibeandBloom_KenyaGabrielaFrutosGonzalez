import gradio as gr
import sys
import os

# Asegurar rutas correctas para importar tus agentes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.agent2_recommender import recomendar_libros_por_vibe

# CSS Avanzado para romper la estructura cuadrada de Gradio y recrear tu mockup premium
luxury_css = """
/* Fondo general con el tono oscuro exacto y tipografía elegante */
body, .gradio-container {
    background: #0D0C0B !important;
    background-image: radial-gradient(circle at top right, #1E1713 0%, #0D0C0B 100%) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* Títulos con Playfair Display estilo Novelia */
.gold-title {
    font-family: 'Playfair Display', serif !important;
    color: #E6D5B8 !important;
    text-align: center;
    font-size: 3.2em;
    font-weight: 700;
    letter-spacing: -1px;
    margin-bottom: 5px;
    text-shadow: 0px 4px 20px rgba(230, 213, 184, 0.15);
}

.gold-subtitle {
    color: #8C8275 !important;
    text-align: center;
    font-size: 1.1em;
    font-style: italic;
    margin-bottom: 40px;
}

/* Simulador de Celular Central (Esquinas súper redondeadas y sombra de lujo) */
.phone-frame {
    background: #161412 !important;
    border: 1px solid #2C2520 !important;
    border-radius: 40px !important;
    padding: 30px 24px !important;
    box-shadow: 0px 25px 50px -12px rgba(0, 0, 0, 0.7) !important;
    margin: 0 auto;
    max-width: 480px;
}

/* Tarjetas laterales con bordes ultra suaves y fondo difuminado */
.luxury-card {
    background: #141210 !important;
    border: 1px solid #241F1B !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3) !important;
}

/* Forzar que los inputs de Gradio pierdan su fondo blanco/gris genérico */
.gradio-container input, .gradio-container textarea {
    background-color: #1A1715 !important;
    border: 1px solid #362E28 !important;
    border-radius: 14px !important;
    color: #F5EFE6 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 12px !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5) !important;
}

.gradio-container input:focus, .gradio-container textarea:focus {
    border-color: #C8A96B !important;
}

/* Botones laterales simulando las Vibes Populares */
.vibe-button {
    background: #1C1815 !important;
    border: 1px solid #2B2420 !important;
    color: #8C8275 !important;
    border-radius: 12px !important;
    text-align: left !important;
    padding: 10px 15px !important;
    transition: all 0.3s ease;
}
.vibe-button:hover {
    background: #26201B !important;
    border-color: #C8A96B !important;
    color: #E6D5B8 !important;
}

/* Botón Principal Dorado de Descubrir */
.gold-action-button {
    background: linear-gradient(135deg, #C8A96B 0%, #A88950 100%) !important;
    color: #0D0C0B !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.5px;
    border: none !important;
    border-radius: 14px !important;
    height: 46px !important;
    box-shadow: 0px 4px 15px rgba(200, 169, 107, 0.3) !important;
    cursor: pointer;
    transition: all 0.3s ease;
}
.gold-action-button:hover {
    transform: translateY(-1px);
    box-shadow: 0px 6px 20px rgba(200, 169, 107, 0.5) !important;
}

/* Ocultar etiquetas feas de Gradio para que se vea limpio como una App nativa */
.block .label {
    color: #C8A96B !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.8em;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
"""

def orquestar_novelia_ui(entrada_usuario):
    if not entrada_usuario.strip():
        return "Bloom está esperando que suspires una vibe...", "Ningún mood detectado todavía."
    
    resultado = recomendar_libros_por_vibe(entrada_usuario)
    
    libros_lista = resultado.get("libros", [])
    libros_texto = ""
    for libro in libros_lista:
        libros_texto += f"📖 {libro}\n\n"
        
    return libros_texto.strip(), resultado.get("explicacion_bloom", "")

with gr.Blocks(css=luxury_css, title="Novelia") as demo:
    
    # Branding superior de lujo
    gr.HTML("<h1 class='gold-title'>Novelia</h1>")
    gr.HTML("<p class='gold-subtitle'>Libros que combinan con tu vibe.</p>")
    
    with gr.Row():
        # ─── COLUMNA IZQUIERDA: MENÚ DE NAVEGACIÓN Y VIBES ───
        with gr.Column(scale=1):
            with gr.Box(elem_classes="luxury-card"):
                gr.Markdown("### 🗂️ NAVEGACIÓN")
                gr.Markdown(
                    """
                    * **📋 Tu Biblioteca**
                      * 📥 Leyendo *(5 libros)*
                      * ⭐ Quiero leer *(12 libros)*
                      * ✓ Leídos *(23 libros)*
                    
                    * **📊 Progreso de lectura**
                      * *24 libros leídos este año*
                      * *8,532 páginas en total*
                    """
                )
            
            gr.Markdown("### 🍂 VIBES POPULARES")
            with gr.Column():
                gr.Button("🕯️ Cozy (Relajante, hogareña)", elem_classes="vibe-button")
                gr.Button("🍁 Nostálgica (Melancólica, emotiva)", elem_classes="vibe-button")
                gr.Button("💖 Romántica (Dulce, intensa)", elem_classes="vibe-button")
                gr.Button("🌙 Misteriosa (Oscura, intrigante)", elem_classes="vibe-button")

        # ─── COLUMNA CENTRAL: EL SMARTPHONE (EL CORAZÓN DE LA APP) ───
        with gr.Column(scale=2):
            with gr.Box(elem_classes="phone-frame"):
                gr.Markdown("## ✨ Hola, Zoe\n¿Qué vibe buscas hoy?")
                
                input_vibe = gr.Textbox(
                    placeholder="Inserta una frase, una canción (ej: Angels Like You), o el mood de un video...",
                    lines=2,
                    show_label=False
                )
                
                btn_descubrir = gr.Button("Descubrir Lecturas ✨", elem_classes="gold-action-button")
                
                gr.Markdown("#### 📚 RECOMENDACIÓN PARA TI")
                output_libros = gr.TextArea(
                    lines=4, 
                    interactive=False,
                    show_label=False
                )
                
                gr.Markdown("#### 🧠 ¿POR QUÉ ESTOS LIBROS? (EXPLICABILIDAD)")
                output_explicacion = gr.TextArea(
                    lines=6, 
                    interactive=False,