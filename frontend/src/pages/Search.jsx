import { useState } from 'react';
import axios from 'axios';

const API = 'https://fantastic-garbanzo-r47j5ppj6x6xf5w9-8000.app.github.dev';

const vibes = [
  { label: 'Cozy', emoji: '☕' },
  { label: 'Nostálgica', emoji: '🍂' },
  { label: 'Misteriosa', emoji: '🌙' },
  { label: 'Romántica', emoji: '🌹' },
  { label: 'Aventurera', emoji: '🗺️' },
  { label: 'Oscura', emoji: '🖤' },
  { label: 'Esperanzadora', emoji: '🌟' },
  { label: 'Melancólica', emoji: '🌧️' },
];

const generos = [
  { label: 'Fantasía', emoji: '🐉' },
  { label: 'Romance', emoji: '💕' },
  { label: 'Ficción', emoji: '✍️' },
  { label: 'Misterio', emoji: '🔍' },
  { label: 'Terror', emoji: '👻' },
  { label: 'Ciencia Ficción', emoji: '🚀' },
];

const Search = () => {
  const [query, setQuery] = useState('');
  const [resultados, setResultados] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [mensajeGuardado, setMensajeGuardado] = useState('');

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const buscarPorVibe = async (vibe) => {
    setCargando(true);
    try {
      const res = await axios.post(`${API}/vibe/texto`, { texto: vibe }, { headers });
      setResultados(res.data.recomendaciones?.libros || []);
    } catch (e) {
      console.error(e);
    }
    setCargando(false);
  };

  const buscarPorTexto = async () => {
    if (!query.trim()) return;
    setCargando(true);
    try {
      const res = await axios.post(`${API}/vibe/texto`, { texto: query }, { headers });
      setResultados(res.data.recomendaciones?.libros || []);
    } catch (e) {
      console.error(e);
    }
    setCargando(false);
  };

  const agregarBiblioteca = async (libro, estado) => {
    try {
      await axios.post(`${API}/biblioteca/agregar`, { libro, estado }, { headers });
      setMensajeGuardado(`"${libro.titulo}" agregado`);
      setTimeout(() => setMensajeGuardado(''), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: '24px 16px 100px' }}>
      <h2 style={{ fontSize: '26px', marginBottom: '20px' }}>Buscar</h2>

      {/* Buscador */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
        <input
          placeholder="Buscar libros, autores, géneros..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && buscarPorTexto()}
          style={{
            flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: '12px', padding: '12px 16px', color: 'var(--text-primary)',
            fontSize: '14px', outline: 'none'
          }}
        />
        <button onClick={buscarPorTexto} style={{
          background: 'var(--accent)', color: 'var(--bg-primary)',
          border: 'none', borderRadius: '12px', padding: '12px 16px',
          fontSize: '14px', cursor: 'pointer', fontWeight: 'bold'
        }}>
          🔍
        </button>
      </div>

      {/* Explorar por vibe */}
      {!resultados.length && !cargando && (
        <>
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <p style={{ fontWeight: 'bold', fontSize: '16px' }}>Explorar por vibe</p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              {vibes.map(v => (
                <button key={v.label} onClick={() => buscarPorVibe(v.label)} style={{
                  background: 'var(--bg-card)', border: '1px solid var(--border)',
                  borderRadius: '14px', padding: '16px', cursor: 'pointer',
                  color: 'var(--text-primary)', fontSize: '14px', fontWeight: '500',
                  display: 'flex', alignItems: 'center', gap: '8px'
                }}>
                  <span style={{ fontSize: '20px' }}>{v.emoji}</span>
                  {v.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '12px' }}>Explorar por géneros</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
              {generos.map(g => (
                <button key={g.label} onClick={() => buscarPorVibe(g.label)} style={{
                  background: 'var(--bg-card)', border: '1px solid var(--border)',
                  borderRadius: '14px', padding: '14px 8px', cursor: 'pointer',
                  color: 'var(--text-primary)', fontSize: '12px', fontWeight: '500',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px'
                }}>
                  <span style={{ fontSize: '22px' }}>{g.emoji}</span>
                  {g.label}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {cargando && (
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px' }}>
          Buscando libros...
        </p>
      )}

      {mensajeGuardado && (
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--accent)',
          borderRadius: '12px', padding: '12px', marginBottom: '16px',
          color: 'var(--accent)', fontSize: '14px', textAlign: 'center'
        }}>
          ✅ {mensajeGuardado}
        </div>
      )}

      {/* Resultados */}
      {resultados.length > 0 && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <p style={{ fontWeight: 'bold', fontSize: '16px' }}>Resultados</p>
            <button onClick={() => setResultados([])} style={{
              background: 'none', border: 'none', color: 'var(--accent)',
              fontSize: '13px', cursor: 'pointer'
            }}>
              Limpiar
            </button>
          </div>

          {resultados.map(libro => (
            <div key={libro.id} style={{
              background: 'var(--bg-card)', borderRadius: '16px',
              padding: '14px', marginBottom: '14px', display: 'flex', gap: '14px'
            }}>
              {libro.portada_url ? (
                <img src={libro.portada_url} alt={libro.titulo}
                  style={{ width: '70px', height: '100px', borderRadius: '8px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{
                  width: '70px', height: '100px', borderRadius: '8px',
                  background: 'var(--bg-modal)', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--text-muted)', fontSize: '10px', textAlign: 'center'
                }}>Sin portada</div>
              )}
              <div style={{ flex: 1 }}>
                <p style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>{libro.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '8px' }}>{libro.autor}</p>
                <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '12px', lineHeight: '1.4' }}>
                  {libro.descripcion?.slice(0, 80)}...
                </p>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <button onClick={() => agregarBiblioteca(libro, 'quiero_leer')} style={btnSmall}>
                    🔖 Quiero leer
                  </button>
                  <button onClick={() => agregarBiblioteca(libro, 'leyendo')} style={btnSmall}>
                    📖 Leyendo
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const btnSmall = {
  background: 'var(--bg-secondary)', color: 'var(--text-secondary)',
  border: '1px solid var(--border)', borderRadius: '10px',
  padding: '6px 10px', fontSize: '12px', cursor: 'pointer'
};

export default Search;