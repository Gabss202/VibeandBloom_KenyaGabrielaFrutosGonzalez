def get_nav_html():
    return """
    <nav class="bottom-nav">
        <div class="nav-item active" onclick="showPage('inicio', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
            </svg>
            Inicio
        </div>
        <div class="nav-item" onclick="showPage('biblioteca', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
            </svg>
            Biblioteca
        </div>
        <div class="nav-item" onclick="showPage('agregar', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            Buscar
        </div>
        <div class="nav-item" onclick="showPage('stats', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
            </svg>
            Perfil
        </div>
    </nav>
    """

def get_header_html():
    return """
    <div class="header">
        <h2 id="page-title">Hola, lectora ✨</h2>
        <div class="header-icon">
            <span></span><span></span><span></span>
        </div>
    </div>
    """