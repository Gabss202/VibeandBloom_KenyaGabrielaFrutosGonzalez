def get_modal_vibe_html():
    return """
    <div class="modal-overlay" id="vibe-modal" onclick="closeModalOutside(event)">
        <div class="modal">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                <div class="modal-title">✦ ¿Qué vibe buscas hoy?</div>
                <button class="modal-close" onclick="closeVibeModal()">✕</button>
            </div>
            <p style="font-size:0.85em; color:var(--text2); margin-bottom:16px; line-height:1.5;">
                Comparte una canción, video, imagen o describe el mood que buscas
            </p>
            <div class="input-types">
                <button class="input-type-btn active" onclick="selectInputType(this, 'Canción')">
                    <span class="icon">🎵</span>Canción
                </button>
                <button class="input-type-btn" onclick="selectInputType(this, 'Video')">
                    <span class="icon">🎬</span>Video
                </button>
                <button class="input-type-btn" onclick="selectInputType(this, 'Imagen')">
                    <span class="icon">🖼️</span>Imagen
                </button>
                <button class="input-type-btn" onclick="selectInputType(this, 'Vibe')">
                    <span class="icon">✨</span>Vibe
                </button>
            </div>
            <textarea id="vibe-input" 
                placeholder="Ej: Algo melancólico pero esperanzador, como una tarde lluviosa con café...">
            </textarea>
            <button class="btn-primary" onclick="getRecommendations()">
                Obtener recomendaciones
            </button>
        </div>
    </div>

    <div class="modal-overlay" id="loading-overlay">
        <div style="text-align:center; color:var(--text);">
            <div class="spinner"></div>
            <p style="font-family:'Playfair Display',serif; font-size:1.1em;">Bloom está pensando...</p>
            <p style="font-size:0.82em; color:var(--text2); margin-top:6px;">Analizando tu vibe ✨</p>
        </div>
    </div>
    """