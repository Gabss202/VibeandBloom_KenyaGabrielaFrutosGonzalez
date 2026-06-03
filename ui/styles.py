COLORS = {
    "bg": "#1C1410",
    "bg2": "#2A1F17", 
    "card": "#2E2218",
    "card2": "#3A2D22",
    "gold": "#C8A96B",
    "gold2": "#8B6B4A",
    "text": "#F5EFE6",
    "text2": "#A89880",
}

CSS_FONTS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap');
"""

CSS_VARIABLES = """
:root {
    --bg: #1C1410;
    --bg2: #2A1F17;
    --card: #2E2218;
    --card2: #3A2D22;
    --gold: #C8A96B;
    --gold2: #8B6B4A;
    --text: #F5EFE6;
    --text2: #A89880;
    --star: #C8A96B;
}
"""

CSS_BASE = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
    background:var(--bg);
    color:var(--text);
    font-family:'Inter',sans-serif;
    max-width:430px;
    margin:0 auto;
    min-height:100vh;
    overflow-x:hidden;
}
"""

CSS_COMPONENTS = """
/* HEADER */
.header { padding:20px 20px 10px; display:flex; justify-content:space-between; align-items:center; }
.header h2 { font-family:'Playfair Display',serif; font-size:1.6em; color:var(--text); }
.header-icon { width:36px; height:36px; display:flex; flex-direction:column; gap:5px; justify-content:center; cursor:pointer; }
.header-icon span { display:block; width:22px; height:2px; background:var(--text); border-radius:2px; }

/* BOTTOM NAV */
.bottom-nav { position:fixed; bottom:0; left:50%; transform:translateX(-50%); width:100%; max-width:430px; background:var(--bg2); border-top:1px solid var(--card2); display:flex; justify-content:space-around; padding:12px 0 20px; z-index:100; }
.nav-item { display:flex; flex-direction:column; align-items:center; gap:4px; cursor:pointer; color:var(--text2); font-size:0.7em; transition:color 0.2s; }
.nav-item.active { color:var(--gold); }
.nav-item svg { width:22px; height:22px; }

/* PAGES */
.page { display:none; padding:0 0 90px 0; }
.page.active { display:block; }

/* BUTTONS */
.btn-primary { width:100%; background:var(--gold2); color:var(--text); border:none; border-radius:12px; padding:14px; font-size:0.95em; font-weight:600; cursor:pointer; transition:background 0.2s; font-family:'Inter',sans-serif; }
.btn-primary:hover { background:var(--gold); color:var(--bg); }

/* CARDS */
.book-cover { width:90px; height:130px; border-radius:10px; background:var(--gold2); display:flex; align-items:center; justify-content:center; font-size:0.75em; color:var(--bg); text-align:center; padding:8px; flex-shrink:0; overflow:hidden; }
.book-cover img { width:100%; height:100%; object-fit:cover; border-radius:10px; }

/* MODAL */
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.7); z-index:200; display:none; align-items:flex-end; }
.modal-overlay.open { display:flex; }
.modal { background:var(--card); border-radius:24px 24px 0 0; padding:24px 20px 40px; width:100%; max-width:430px; margin:0 auto; }
.modal-title { font-family:'Playfair Display',serif; font-size:1.3em; color:var(--gold); }
.modal-close { background:none; border:none; color:var(--text2); font-size:1.4em; cursor:pointer; }

/* INPUTS */
textarea, input[type=text], input[type=number], select {
    width:100%; background:var(--card2); border:1px solid var(--card2);
    border-radius:10px; padding:12px 14px; color:var(--text);
    font-family:'Inter',sans-serif; font-size:0.9em; outline:none;
}
textarea { resize:none; height:120px; }
textarea::placeholder, input::placeholder { color:var(--text2); }
select option { background:var(--card2); }

/* LOADING */
.spinner { width:30px; height:30px; border:2px solid var(--card2); border-top:2px solid var(--gold); border-radius:50%; animation:spin 1s linear infinite; margin:0 auto 10px; }
@keyframes spin { to { transform:rotate(360deg); } }

/* MISC */
.vibe-tag { background:transparent; border:1px solid var(--gold2); color:var(--gold); padding:3px 10px; border-radius:20px; font-size:0.75em; }
.vibe-tags { display:flex; flex-wrap:wrap; gap:6px; margin-top:12px; }
.empty-state { text-align:center; padding:40px 20px; color:var(--text2); }
.empty-state .emoji { font-size:2.5em; margin-bottom:10px; }
.msg { padding:10px 14px; border-radius:10px; font-size:0.85em; margin-bottom:14px; display:none; }
.msg.success { background:#1a3a1a; color:#7ec87e; display:block; }
.msg.error { background:#3a1a1a; color:#c87e7e; display:block; }
"""

CSS_INICIO = """
.vibe-section { padding:16px 20px; }
.vibe-section h3 { font-size:0.9em; color:var(--text2); margin-bottom:14px; }
.vibe-buttons { display:flex; gap:12px; margin-bottom:20px; }
.vibe-btn { display:flex; flex-direction:column; align-items:center; gap:6px; cursor:pointer; }
.vibe-btn-circle { width:56px; height:56px; border-radius:50%; background:var(--card2); display:flex; align-items:center; justify-content:center; font-size:1.4em; transition:background 0.2s; }
.vibe-btn:hover .vibe-btn-circle { background:var(--gold2); }
.vibe-btn span { font-size:0.72em; color:var(--text2); }
.recommendation-card { margin:0 20px; background:var(--card); border-radius:16px; padding:16px; border:1px solid var(--card2); }
.rec-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; }
.rec-header span { font-size:0.85em; color:var(--text2); }
.rec-book { display:flex; gap:14px; }
.book-info .book-title { font-family:'Playfair Display',serif; font-size:1.15em; line-height:1.3; margin-bottom:4px; }
.book-info .book-author { font-size:0.82em; color:var(--text2); margin-bottom:8px; }
.stars { color:var(--star); font-size:0.9em; }
.why-section { margin-top:14px; padding-top:14px; border-top:1px solid var(--card2); }
.why-section h4 { font-size:0.82em; color:var(--text2); margin-bottom:6px; }
.why-section p { font-size:0.85em; line-height:1.5; }
.results-section { padding:16px 20px; display:none; }
.results-section.show { display:block; }
.result-book-card { background:var(--card); border-radius:14px; padding:14px; display:flex; gap:12px; margin-bottom:10px; border:1px solid var(--card2); }
.result-book-cover { width:60px; height:85px; border-radius:8px; background:var(--gold2); flex-shrink:0; overflow:hidden; display:flex; align-items:center; justify-content:center; font-size:0.7em; color:var(--bg); text-align:center; padding:4px; }
.result-book-cover img { width:100%; height:100%; object-fit:cover; }
.result-book-info h4 { font-family:'Playfair Display',serif; font-size:1em; margin-bottom:3px; }
.result-book-info .author { font-size:0.8em; color:var(--text2); }
.bloom-text { background:var(--card); border-radius:14px; padding:14px; margin-bottom:16px; border-left:3px solid var(--gold); font-size:0.88em; line-height:1.6; color:var(--text2); font-style:italic; }
"""

CSS_BIBLIOTECA = """
.lib-tabs { display:flex; padding:0 20px; border-bottom:1px solid var(--card2); margin-bottom:16px; }
.lib-tab { flex:1; text-align:center; padding:12px 0; font-size:0.88em; color:var(--text2); cursor:pointer; border-bottom:2px solid transparent; transition:all 0.2s; }
.lib-tab.active { color:var(--gold); border-bottom-color:var(--gold); }
.lib-books { padding:0 20px; }
.lib-book-card { background:var(--card); border-radius:14px; padding:14px; display:flex; gap:12px; margin-bottom:10px; }
.lib-book-cover { width:70px; height:100px; border-radius:10px; background:var(--gold2); flex-shrink:0; overflow:hidden; display:flex; align-items:center; justify-content:center; font-size:0.72em; color:var(--bg); text-align:center; padding:4px; }
.lib-book-cover img { width:100%; height:100%; object-fit:cover; }
.lib-book-info h4 { font-family:'Playfair Display',serif; font-size:1em; margin-bottom:3px; }
.lib-book-info .author { font-size:0.8em; color:var(--text2); margin-bottom:8px; }
.progress-bar { background:var(--card2); border-radius:4px; height:4px; margin-top:6px; }
.progress-fill { height:100%; border-radius:4px; background:var(--gold); }
.progress-text { font-size:0.75em; color:var(--text2); margin-top:4px; }
"""

CSS_AGREGAR = """
.add-form { padding:0 20px; }
.form-group { margin-bottom:14px; }
.form-group label { display:block; font-size:0.82em; color:var(--text2); margin-bottom:6px; }
.status-selector { display:flex; gap:8px; }
.status-btn { flex:1; background:var(--card2); border:none; border-radius:10px; padding:10px 6px; text-align:center; cursor:pointer; font-size:0.8em; color:var(--text2); transition:all 0.2s; }
.status-btn.active { background:var(--gold2); color:var(--text); }
"""

CSS_EXTRAS = """
.search-tabs { display:flex; padding:0 20px; border-bottom:1px solid var(--card2); margin-bottom:16px; }
.search-tab { flex:1; text-align:center; padding:12px 0; font-size:0.88em; color:var(--text2); cursor:pointer; border-bottom:2px solid transparent; transition:all 0.2s; }
.search-tab.active { color:var(--gold); border-bottom-color:var(--gold); }
.search-panel { display:none; }
.search-panel.active { display:block; }
.search-input-wrap { display:flex; align-items:center; gap:10px; background:var(--card2); border-radius:12px; padding:0 14px; }
.search-input-wrap input { background:transparent; border:none; padding:12px 0; flex:1; }
.stat-num { font-family:'Playfair Display',serif; font-size:1.8em; color:var(--gold); margin-bottom:4px; }
.profile-menu-item { display:flex; align-items:center; gap:14px; padding:16px 0; border-bottom:1px solid var(--card2); cursor:pointer; color:var(--text); }
.profile-menu-item span { flex:1; font-size:0.92em; }
"""

CSS_MODAL_VIBE = """
.input-types { display:flex; gap:10px; margin-bottom:16px; }
.input-type-btn { flex:1; background:var(--card2); border:none; border-radius:12px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:6px; cursor:pointer; color:var(--text); font-size:0.75em; transition:background 0.2s; }
.input-type-btn:hover, .input-type-btn.active { background:var(--gold2); }
.input-type-btn span.icon { font-size:1.4em; }
"""

def get_full_css():
    return (CSS_FONTS + CSS_VARIABLES + CSS_BASE + CSS_COMPONENTS +
            CSS_INICIO + CSS_BIBLIOTECA + CSS_AGREGAR + CSS_STATS + CSS_MODAL_VIBE + CSS_EXTRAS)