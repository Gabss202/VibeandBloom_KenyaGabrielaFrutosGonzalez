def get_biblioteca_html():
    return """
    <div class="page" id="page-biblioteca">
        <div class="lib-tabs">
            <div class="lib-tab active" onclick="filterLib('leyendo', this)">Leyendo</div>
            <div class="lib-tab" onclick="filterLib('quiero_leer', this)">Quiero leer</div>
            <div class="lib-tab" onclick="filterLib('leido', this)">Leidos</div>
        </div>
        <div class="lib-books" id="lib-books-list">
            <div class="empty-state">
                <div class="emoji">📚</div>
                <p>Cargando tu biblioteca...</p>
            </div>
        </div>
    </div>
    """

def get_agregar_html():
    return """
    <div class="page" id="page-agregar">
        <div class="search-tabs">
            <div class="search-tab active" onclick="switchSearchTab('buscar', this)">Buscar</div>
            <div class="search-tab" onclick="switchSearchTab('agregar', this)">Agregar</div>
        </div>

        <!-- PANEL BUSCAR -->
        <div id="panel-buscar" class="search-panel active">
            <div class="add-form">
                <div class="form-group">
                    <div class="search-input-wrap">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text2)" stroke-width="2">
                            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                        </svg>
                        <input type="text" id="search-query" placeholder="Buscar por titulo, autor o genero..." 
                               oninput="searchBooks(this.value)">
                    </div>
                </div>
                <div id="search-results-list"></div>
            </div>
        </div>

        <!-- PANEL AGREGAR -->
        <div id="panel-agregar" class="search-panel">
            <div class="add-form">
                <div id="add-msg" class="msg"></div>
                <div class="form-group">
                    <label>Titulo *</label>
                    <input type="text" id="add-title" placeholder="A Court of Thorns and Roses">
                </div>
                <div class="form-group">
                    <label>Autor *</label>
                    <input type="text" id="add-author" placeholder="Sarah J. Maas">
                </div>
                <div class="form-group">
                    <label>Genero</label>
                    <select id="add-genre">
                        <option value="">Selecciona un genero</option>
                        <option value="dark romance">Dark Romance</option>
                        <option value="fantasia">Fantasia</option>
                        <option value="contemporaneo">Contemporaneo</option>
                        <option value="misterio">Misterio</option>
                        <option value="thriller">Thriller</option>
                        <option value="ciencia ficcion">Ciencia Ficcion</option>
                        <option value="clasico">Clasico</option>
                        <option value="cozy fiction">Cozy Fiction</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Estado</label>
                    <div class="status-selector">
                        <button class="status-btn active" onclick="setStatus('quiero_leer', this)">🔖 Quiero leer</button>
                        <button class="status-btn" onclick="setStatus('leyendo', this)">📖 Leyendo</button>
                        <button class="status-btn" onclick="setStatus('leido', this)">✅ Leido</button>
                    </div>
                </div>
                <button class="btn-primary" onclick="addBook()">Agregar a mi biblioteca 🌸</button>

                <div style="margin:24px 0 16px; border-top:1px solid var(--card2); padding-top:20px;">
                    <h3 style="font-family:'Playfair Display',serif; font-size:1.1em; margin-bottom:4px;">Escribir resena</h3>
                    <p style="font-size:0.82em; color:var(--text2);">Ya terminaste un libro? Cuentanos</p>
                </div>
                <div class="form-group">
                    <label>ID del libro (ver biblioteca)</label>
                    <input type="number" id="rev-id" placeholder="1">
                </div>
                <div class="form-group">
                    <label>Calificacion: <span id="rating-val">4</span> ★</label>
                    <input type="range" min="1" max="5" step="0.5" value="4" id="rev-rating"
                        oninput="document.getElementById('rating-val').textContent=this.value"
                        style="width:100%; accent-color:var(--gold); margin-top:6px;">
                </div>
                <div class="form-group">
                    <label>Que te parecio?</label>
                    <textarea id="rev-text" placeholder="Comparte tu opinion sobre este libro..."></textarea>
                </div>
                <div class="form-group">
                    <label>Personajes favoritos</label>
                    <input type="text" id="rev-chars" placeholder="Rhysand, Feyre...">
                </div>
                <div class="form-group">
                    <label>Musica que te recuerda</label>
                    <input type="text" id="rev-music" placeholder="Cruel Summer - Taylor Swift">
                </div>
                <div class="form-group">
                    <label>Vibes</label>
                    <input type="text" id="rev-vibes" placeholder="enemies to lovers, dark romance...">
                </div>
                <div id="rev-msg" class="msg"></div>
                <button class="btn-primary" onclick="addReview()">Publicar resena</button>
            </div>
        </div>
    </div>
    """

def get_stats_html():
    return """
    <div class="page" id="page-stats">
        <div style="padding:0 20px 16px;">
            <h2 style="font-family:'Playfair Display',serif; font-size:1.4em;">Perfil</h2>
        </div>

        <!-- PERFIL -->
        <div style="padding:0 20px; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px;">
                <div style="width:70px; height:70px; border-radius:50%; background:var(--gold2); display:flex; align-items:center; justify-content:center; font-size:1.8em;">🌿</div>
                <div>
                    <div style="font-family:'Playfair Display',serif; font-size:1.2em;">Lectora</div>
                    <div style="font-size:0.82em; color:var(--text2);">@novelia</div>
                </div>
            </div>
        </div>

        <!-- STATS GRID -->
        <div class="stats-grid" id="stats-grid">
            <div class="stat-card"><div class="stat-num">-</div><div class="label">Libros leidos</div></div>
            <div class="stat-card"><div class="stat-num">-</div><div class="label">Calificacion prom.</div></div>
            <div class="stat-card"><div class="stat-num">-</div><div class="label">Leyendo ahora</div></div>
            <div class="stat-card"><div class="stat-num">-</div><div class="label">Por leer</div></div>
        </div>

        <!-- GENEROS -->
        <div class="genres-section">
            <h3>Generos favoritos</h3>
            <div id="genres-list">
                <div style="color:var(--text2); font-size:0.85em;">Agrega libros para ver tus generos</div>
            </div>
        </div>

        <!-- INSIGHT -->
        <div class="insight-card">
            <p id="insight-text">Cargando tu analisis lector...</p>
        </div>

        <!-- MENU PERFIL -->
        <div style="padding:0 20px; margin-top:8px;">
            <div class="profile-menu-item" onclick="loadStats()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
                </svg>
                <span>Actualizar estadisticas</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                </svg>
            </div>
            <div class="profile-menu-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
                </svg>
                <span>Configuracion</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                </svg>
            </div>
            <div class="profile-menu-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                <span style="color:#c87e7e;">Cerrar sesion</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#c87e7e" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                </svg>
            </div>
        </div>
    </div>
    """