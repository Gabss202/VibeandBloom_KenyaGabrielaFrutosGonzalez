def get_inicio_html():
    return """
    <div class="page active" id="page-inicio">
        <div class="vibe-section">
            <h3>¿Qué vibe buscas hoy?</h3>
            <div class="vibe-buttons">
                <div class="vibe-btn" onclick="openVibeModal('🎵 Canción')">
                    <div class="vibe-btn-circle">🎵</div>
                    <span>Canción</span>
                </div>
                <div class="vibe-btn" onclick="openVibeModal('🎬 Video')">
                    <div class="vibe-btn-circle">🎬</div>
                    <span>Video</span>
                </div>
                <div class="vibe-btn" onclick="openVibeModal('🖼️ Imagen')">
                    <div class="vibe-btn-circle">🖼️</div>
                    <span>Imagen</span>
                </div>
                <div class="vibe-btn" onclick="openVibeModal('✨ Vibe')">
                    <div class="vibe-btn-circle">✨</div>
                    <span>Vibe</span>
                </div>
            </div>
        </div>

        <div class="recommendation-card" id="featured-card">
            <div class="rec-header">
                <span>Recomendación para ti</span>
                <span>🔖</span>
            </div>
            <div class="rec-book">
                <div class="book-cover" id="featured-cover">Portada del libro</div>
                <div class="book-info">
                    <div class="book-title" id="featured-title">Descubre tu próxima lectura</div>
                    <div class="book-author" id="featured-author">Describe una vibe para comenzar</div>
                    <div class="stars">★★★★★</div>
                </div>
            </div>
            <div class="why-section">
                <h4>¿Por qué este libro?</h4>
                <p id="featured-why">Toca uno de los botones de vibe para recibir recomendaciones ✨</p>
            </div>
            <div class="vibe-tags" id="featured-tags">
                <span class="vibe-tag">tu vibe</span>
                <span class="vibe-tag">tus libros</span>
            </div>
        </div>

        <div class="results-section" id="results-section">
            <h3 style="font-family:'Playfair Display',serif; padding:0 0 12px 0; font-size:1em;">
                También podrían gustarte
            </h3>
            <div id="results-list"></div>
        </div>
    </div>
    """