JS_CODE = r"""
const API = '';

function showPage(page, el) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');
    el.classList.add('active');
    const titles = { inicio: 'Hola, lectora', biblioteca: 'Mi biblioteca', agregar: 'Buscar', stats: 'Perfil' };
    document.getElementById('page-title').textContent = titles[page];
    if (page === 'biblioteca') loadLibrary('leyendo');
    if (page === 'stats') loadStats();
}

let selectedType = 'Cancion';
function openVibeModal(type) {
    document.getElementById('vibe-modal').classList.add('open');
    document.getElementById('vibe-input').value = '';
}
function closeVibeModal() { document.getElementById('vibe-modal').classList.remove('open'); }
function closeModalOutside(e) { if (e.target.id === 'vibe-modal') closeVibeModal(); }
function selectInputType(btn, type) {
    document.querySelectorAll('.input-type-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedType = type;
}

async function getRecommendations() {
    const input = document.getElementById('vibe-input').value.trim();
    if (!input) return;
    closeVibeModal();
    document.getElementById('loading-overlay').classList.add('open');
    try {
        const res = await fetch(API + '/api/recomendar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ descripcion: selectedType + ': ' + input })
        });
        const data = await res.json();
        displayRecommendations(data);
    } catch(e) {
        alert('Error conectando con el servidor');
    } finally {
        document.getElementById('loading-overlay').classList.remove('open');
    }
}

function displayRecommendations(data) {
    const libros = data.libros || [];
    const explicacion = data.explicacion_bloom || '';
    const tags = data.generos_deducidos || [];

    if (libros.length > 0) {
        const parts = libros[0].split(' - ');
        const titulo = parts[0];
        const autor = parts[1] || '';
        document.getElementById('featured-title').textContent = titulo;
        document.getElementById('featured-author').textContent = autor;
        document.getElementById('featured-why').textContent = explicacion.substring(0, 150) + '...';
        document.getElementById('featured-cover').innerHTML = '<span>' + titulo.substring(0,20) + '</span>';
        fetchCover(titulo, autor, 'featured-cover');
    }

    document.getElementById('featured-tags').innerHTML = tags.map(function(t) {
        return '<span class="vibe-tag">' + t + '</span>';
    }).join('');

    const list = document.getElementById('results-list');
    list.innerHTML = '';
    libros.slice(1).forEach(function(libro) {
        const parts = libro.split(' - ');
        const titulo = parts[0];
        const autor = parts[1] || '';
        const id = 'cover-' + titulo.substring(0,8).replace(/\s/g,'');
        const card = document.createElement('div');
        card.className = 'result-book-card';
        card.innerHTML = '<div class="result-book-cover" id="' + id + '">' + titulo.substring(0,15) + '</div>' +
            '<div class="result-book-info">' +
            '<h4>' + titulo + '</h4>' +
            '<div class="author">' + autor + '</div>' +
            '<div class="vibe-tags" style="margin-top:6px;">' +
            tags.map(function(t) { return '<span class="vibe-tag">' + t + '</span>'; }).join('') +
            '</div></div>';
        list.appendChild(card);
        setTimeout(function() { fetchCover(titulo, autor, id); }, 100);
    });

    document.getElementById('results-section').classList.add('show');
}

async function fetchCover(title, author, elId) {
    try {
        const q = encodeURIComponent(title + ' ' + author);
        const res = await fetch('https://openlibrary.org/search.json?q=' + q + '&limit=1');
        const data = await res.json();
        if (data.docs && data.docs[0] && data.docs[0].cover_i) {
            const url = 'https://covers.openlibrary.org/b/id/' + data.docs[0].cover_i + '-M.jpg';
            const el = document.getElementById(elId);
            if (el) el.innerHTML = '<img src="' + url + '" alt="' + title + '">';
        }
    } catch(e) {}
}

async function loadLibrary(status) {
    const list = document.getElementById('lib-books-list');
    list.innerHTML = '<div class="empty-state"><div class="spinner" style="width:24px;height:24px;border:2px solid #333;border-top:2px solid var(--gold);border-radius:50%;animation:spin 1s linear infinite;margin:20px auto;"></div></div>';
    try {
        const url = API + '/api/biblioteca' + (status ? '?status=' + status : '');
        const res = await fetch(url);
        const libros = await res.json();
        if (!libros.length) {
            list.innerHTML = '<div class="empty-state"><div class="emoji">-</div><p>No hay libros aqui todavia</p></div>';
            return;
        }
        list.innerHTML = libros.map(function(l) {
            const estrellas = l.rating ? ('*').repeat(Math.round(l.rating)) : '';
            const covId = 'lib-cover-' + l.id;
            setTimeout(function() { if(l.title && l.author) fetchCover(l.title, l.author, covId); }, 100);
            return '<div class="lib-book-card">' +
                '<div class="lib-book-cover" id="' + covId + '">' + (l.title ? l.title.substring(0,15) : '') + '</div>' +
                '<div class="lib-book-info">' +
                '<h4>' + l.title + '</h4>' +
                '<div class="author">' + l.author + '</div>' +
                (l.rating ? '<div style="font-size:0.85em;color:var(--gold);">' + '★'.repeat(Math.round(l.rating)) + '</div>' : '') +
                (l.status === 'leyendo' ? '<div class="progress-bar"><div class="progress-fill" style="width:45%"></div></div><div class="progress-text">En progreso</div>' : '') +
                (l.review_text ? '<div style="font-size:0.78em;color:var(--text2);margin-top:4px;font-style:italic;">"' + l.review_text.substring(0,60) + '..."</div>' : '') +
                '</div></div>';
        }).join('');
    } catch(e) {
        list.innerHTML = '<div class="empty-state"><p>Error cargando biblioteca</p></div>';
    }
}

function filterLib(status, el) {
    document.querySelectorAll('.lib-tab').forEach(function(t) { t.classList.remove('active'); });
    el.classList.add('active');
    loadLibrary(status);
}

let currentStatus = 'quiero_leer';
function setStatus(status, btn) {
    currentStatus = status;
    document.querySelectorAll('.status-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
}

async function addBook() {
    const title = document.getElementById('add-title').value.trim();
    const author = document.getElementById('add-author').value.trim();
    const genre = document.getElementById('add-genre').value;
    const msg = document.getElementById('add-msg');
    if (!title || !author) { showMsg(msg, 'Titulo y autor son obligatorios', 'error'); return; }
    try {
        const res = await fetch(API + '/api/agregar-libro', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title: title, author: author, genre: genre, status: currentStatus, total_pages: 0 })
        });
        const data = await res.json();
        showMsg(msg, data.mensaje, data.exito ? 'success' : 'error');
        if (data.exito) {
            document.getElementById('add-title').value = '';
            document.getElementById('add-author').value = '';
        }
    } catch(e) { showMsg(msg, 'Error de conexion', 'error'); }
}

async function addReview() {
    const book_id = parseInt(document.getElementById('rev-id').value);
    const rating = parseFloat(document.getElementById('rev-rating').value);
    const review_text = document.getElementById('rev-text').value;
    const msg = document.getElementById('rev-msg');
    if (!book_id) { showMsg(msg, 'Ingresa el ID del libro', 'error'); return; }
    try {
        const res = await fetch(API + '/api/agregar-resena', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                book_id: book_id,
                rating: rating,
                review_text: review_text,
                favorite_characters: document.getElementById('rev-chars').value,
                music: document.getElementById('rev-music').value,
                vibes: document.getElementById('rev-vibes').value
            })
        });
        const data = await res.json();
        showMsg(msg, data.mensaje, data.exito ? 'success' : 'error');
    } catch(e) { showMsg(msg, 'Error de conexion', 'error'); }
}

async function loadStats() {
    try {
        const res = await fetch(API + '/api/estadisticas');
        const s = await res.json();
        document.getElementById('stats-grid').innerHTML =
            '<div class="stat-card"><div class="stat-icon">&#128214;</div><div class="number">' + s.total_leidos + '</div><div class="label">Libros leidos</div></div>' +
            '<div class="stat-card"><div class="stat-icon">&#11088;</div><div class="number">' + (s.promedio_calificacion || '-') + '</div><div class="label">Calificacion promedio</div></div>' +
            '<div class="stat-card"><div class="stat-icon">&#128218;</div><div class="number">' + s.total_leyendo + '</div><div class="label">Leyendo ahora</div></div>' +
            '<div class="stat-card"><div class="stat-icon">&#128278;</div><div class="number">' + s.total_quiero_leer + '</div><div class="label">Por leer</div></div>';
        document.getElementById('insight-text').textContent = s.insight || 'Sigue leyendo para ver tu analisis';
        if (s.genero_favorito && s.genero_favorito !== 'Sin datos') {
            document.getElementById('genres-list').innerHTML =
                '<div class="genre-bar">' +
                '<div class="genre-bar-header"><span>' + s.genero_favorito + '</span><span>' + s.total_leidos + ' libros</span></div>' +
                '<div class="genre-progress"><div class="genre-progress-fill" style="width:80%"></div></div>' +
                '</div>';
        }
    } catch(e) {}
}

function showMsg(el, text, type) {
    el.textContent = text;
    el.className = 'msg ' + type;
    setTimeout(function() { el.className = 'msg'; }, 4000);
}

function switchSearchTab(tab, el) {
    document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.search-panel').forEach(p => p.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('panel-' + tab).classList.add('active');
}

async function searchBooks(query) {
    const list = document.getElementById('search-results-list');
    if (!query || query.length < 2) { list.innerHTML = ''; return; }
    try {
        const q = encodeURIComponent(query);
        const res = await fetch('https://openlibrary.org/search.json?q=' + q + '&limit=8&language=spa');
        const data = await res.json();
        if (!data.docs || !data.docs.length) {
            list.innerHTML = '<div class="empty-state"><p>No se encontraron resultados</p></div>';
            return;
        }
        list.innerHTML = data.docs.map(function(book) {
            const title = book.title || '';
            const author = book.author_name ? book.author_name[0] : 'Autor desconocido';
            const year = book.first_publish_year || '';
            const coverId = book.cover_i ? 'cover-search-' + book.cover_i : null;
            const coverHtml = coverId
                ? '<div class="result-book-cover" id="' + coverId + '"><img src="https://covers.openlibrary.org/b/id/' + book.cover_i + '-S.jpg" style="width:100%;height:100%;object-fit:cover;"></div>'
                : '<div class="result-book-cover">' + title.substring(0,10) + '</div>';
            return '<div class="result-book-card">' + coverHtml +
                '<div class="result-book-info">' +
                '<h4>' + title + '</h4>' +
                '<div class="author">' + author + (year ? ' · ' + year : '') + '</div>' +
                '<button onclick="quickAdd(\'' + title.replace(/'/g,"\\'") + '\',\'' + author.replace(/'/g,"\\'") + '\')" ' +
                'style="margin-top:8px;background:var(--gold2);border:none;color:var(--text);padding:5px 12px;border-radius:8px;font-size:0.78em;cursor:pointer;">+ Agregar</button>' +
                '</div></div>';
        }).join('');
    } catch(e) {
        list.innerHTML = '<div class="empty-state"><p>Error buscando libros</p></div>';
    }
}

async function quickAdd(title, author) {
    try {
        const res = await fetch(API + '/api/agregar-libro', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title: title, author: author, genre: '', status: 'quiero_leer', total_pages: 0 })
        });
        const data = await res.json();
        alert(data.mensaje);
    } catch(e) { alert('Error agregando libro'); }
}
"""