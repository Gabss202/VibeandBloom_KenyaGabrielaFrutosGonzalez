import { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import API from '../config';

const vibes = [
  { label: 'Cozy', emoji: '☕', color: '#8B6914' },
  { label: 'Nostálgica', emoji: '🍁', color: '#7D4E2D' },
  { label: 'Misteriosa', emoji: '🕯️', color: '#3D3560' },
  { label: 'Romántica', emoji: '💘', color: '#7D2D3F' },
  { label: 'Aventurera', emoji: '🗺️', color: '#2D5A3F' },
  { label: 'Oscura', emoji: '🌑', color: '#2D2D2D' },
  { label: 'Esperanzadora', emoji: '🌤️', color: '#6B5A2D' },
  { label: 'Melancólica', emoji: '🌧️', color: '#2D4A6B' },
];

const generos = [
  { label: 'Fantasía', emoji: '🧙' },
  { label: 'Romance', emoji: '💘' },
  { label: 'Ficción', emoji: '📚' },
  { label: 'Misterio', emoji: '🕵️' },
  { label: 'Terror', emoji: '👻' },
  { label: 'Sci-Fi', emoji: '🚀' },
];

const Search = () => {
  const [query, setQuery] = useState('');
  const [resultados, setResultados] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [mensajeGuardado, setMensajeGuardado] = useState('');
  const [analisisVibe, setAnalisisVibe] = useState(null);
  const [libroSeleccionado, setLibroSeleccionado] = useState(null);
  const [vibeActivo, setVibeActivo] = useState(null);
  const [estadosGuardados, setEstadosGuardados] = useState({});

  const token = localStorage.getItem('token');
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const cargarEstadosBiblioteca = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/biblioteca`, { headers });
      const estados = {};
      res.data?.leyendo?.forEach(libro => { estados[libro.id] = 'leyendo'; });
      res.data?.quiero_leer?.forEach(libro => { estados[libro.id] = 'quiero_leer'; });
      res.data?.leidos?.forEach(libro => { estados[libro.id] = 'leido'; });
      setEstadosGuardados(estados);
    } catch (e) {
      console.error(e);
    }
  }, [headers]);

  useEffect(() => {
    cargarEstadosBiblioteca();
  }, [cargarEstadosBiblioteca]);

  const buscar = async (texto) => {
    setCargando(true);
    setResultados([]);
    setAnalisisVibe(null);
    try {
      const res = await axios.get(`${API}/libros/buscar`, { headers, params: { q: texto } });
      const libros = res.data?.libros || [];
      setResultados(libros);
      setAnalisisVibe({
        vibe: texto,
        tags: [texto],
        explicacion: `Busqué títulos relacionados con '${texto}' y ordené resultados que coinciden con ese género o mood.`,
        inferencias: [`Se priorizaron libros cercanos al término '${texto}'.`],
        total: libros.length,
      });
    } catch (e) {
      console.error(e);
    }
    setCargando(false);
  };

  const buscarPorVibe = (vibe) => {
    setVibeActivo(vibe);
    buscar(vibe);
  };

  const buscarPorTexto = () => {
    if (!query.trim()) return;
    setVibeActivo(null);
    buscar(query);
  };

  const agregarBiblioteca = async (libro, estado) => {
    try {
      const res = await axios.post(`${API}/biblioteca/agregar`, { libro, estado }, { headers });
      const mensaje = res.data?.mensaje || `"${libro.titulo}" agregado`;
      setMensajeGuardado(res.data?.sugerencia ? `${mensaje}. ${res.data.sugerencia}` : mensaje);
      await cargarEstadosBiblioteca();
      setLibroSeleccionado(null);
      setTimeout(() => setMensajeGuardado(''), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: '24px 16px 100px', maxWidth: '480px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '20px' }}>Buscar</h2>

      {/* Buscador */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '28px' }}>
        <input
          placeholder="Buscar libros, autores, géneros..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && buscarPorTexto()}
          style={{
            flex: 1, background: 'var(--bg-card)',
            border: '1px solid var(--border)', borderRadius: '14px',
            padding: '13px 16px', color: 'var(--text-primary)',
            fontSize: '14px', outline: 'none'
          }}
        />
        <button onClick={buscarPorTexto} style={{
          background: 'var(--accent)', color: 'var(--bg-primary)',
          border: 'none', borderRadius: '14px', padding: '13px 18px',
          fontSize: '16px', cursor: 'pointer'
        }}>Buscar</button>
      </div>

      {!resultados.length && !cargando && (
        <>
          {/* Vibes */}
          <div style={{ marginBottom: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <p style={{ fontWeight: 'bold', fontSize: '16px' }}>Explorar por vibe</p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              {vibes.map(v => (
                <button key={v.label} onClick={() => buscarPorVibe(v.label)} style={{
                  background: 'var(--bg-card)', border: '1px solid var(--border)',
                  borderRadius: '16px', padding: '18px 14px', cursor: 'pointer',
                  color: 'var(--text-primary)', fontSize: '14px', fontWeight: '500',
                  display: 'flex', alignItems: 'center', gap: '10px',
                  textAlign: 'left', transition: 'background 0.2s'
                }}>
                  <span style={{ fontSize: '22px' }}>{v.emoji}</span>
                  {v.label}
                </button>
              ))}
            </div>
          </div>

          {/* Géneros */}
          <div>
            <p style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '14px' }}>Explorar por géneros</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
              {generos.map(g => (
                <button key={g.label} onClick={() => buscarPorVibe(g.label)} style={{
                  background: 'var(--bg-card)', border: '1px solid var(--border)',
                  borderRadius: '16px', padding: '16px 8px', cursor: 'pointer',
                  color: 'var(--text-primary)', fontSize: '12px', fontWeight: '500',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px'
                }}>
                  <span style={{ fontSize: '24px' }}>{g.emoji}</span>
                  {g.label}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {cargando && (
        <div style={{ textAlign: 'center', marginTop: '60px' }}>
          <p style={{ fontSize: '32px', marginBottom: '12px' }}>Buscando</p>
          <p style={{ color: 'var(--text-muted)' }}>Buscando libros perfectos para ti...</p>
        </div>
      )}

      {mensajeGuardado && (
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--accent)',
          borderRadius: '14px', padding: '12px', marginBottom: '16px',
          color: 'var(--accent)', fontSize: '14px', textAlign: 'center'
        }}>{mensajeGuardado}</div>
      )}

      {resultados.length > 0 && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <p style={{ fontWeight: 'bold', fontSize: '16px' }}>
              {vibeActivo ? `Vibe: ${vibeActivo}` : 'Resultados'}
            </p>
            <button onClick={() => { setResultados([]); setVibeActivo(null); setAnalisisVibe(null); }} style={{
              background: 'none', border: 'none', color: 'var(--accent)',
              fontSize: '13px', cursor: 'pointer'
            }}>← Volver</button>
          </div>

          {analisisVibe && (
            <div style={{
              background: 'var(--bg-card)', borderRadius: '18px',
              padding: '16px', marginBottom: '16px',
              border: '1px solid var(--border)'
            }}>
              <p style={{ color: 'var(--accent)', fontWeight: 'bold', fontSize: '13px', marginBottom: '8px' }}>
                Por qué estas recomendaciones
              </p>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '1.5', marginBottom: '10px' }}>
                {analisisVibe.explicacion || 'El sistema detectó señales suficientes para ajustar géneros y priorizar libros afines.'}
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '10px' }}>
                {analisisVibe.tags.map(tag => (
                  <span key={tag} style={{
                    background: 'var(--bg-modal)', color: 'var(--text-secondary)',
                    padding: '4px 10px', borderRadius: '999px', fontSize: '12px'
                  }}>{tag}</span>
                ))}
              </div>
              {analisisVibe.inferencias.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {analisisVibe.inferencias.map(inferencia => (
                    <p key={inferencia} style={{ color: 'var(--text-secondary)', fontSize: '12px', lineHeight: '1.5' }}>
                      • {inferencia}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}

          {resultados.map(libro => (
            <div key={libro.id} onClick={() => setLibroSeleccionado(libro)} style={{
              background: 'var(--bg-card)', borderRadius: '18px',
              padding: '14px', marginBottom: '12px',
              display: 'flex', gap: '14px', cursor: 'pointer',
              border: '1px solid var(--border)'
            }}>
              {libro.portada_url ? (
                <img src={libro.portada_url} alt={libro.titulo}
                  style={{ width: '65px', height: '95px', borderRadius: '8px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{
                  width: '65px', height: '95px', borderRadius: '8px',
                  background: 'var(--bg-modal)', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px'
                }}>LIB</div>
              )}
              <div style={{ flex: 1 }}>
                <p style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px', lineHeight: '1.3' }}>{libro.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '8px' }}>{libro.autor}</p>
                {estadosGuardados[libro.id] && (
                  <p style={{ color: 'var(--accent)', fontSize: '11px', marginBottom: '8px', fontWeight: 'bold' }}>
                    Guardado como: {estadosGuardados[libro.id].replace('_', ' ')}
                  </p>
                )}
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'quiero_leer'); }} style={btnSmall}>
                    Quiero leer
                  </button>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'leyendo'); }} style={btnSmall}>
                    Leyendo
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal detalle */}
      {libroSeleccionado && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)',
          display: 'flex', alignItems: 'flex-end', zIndex: 200
        }} onClick={() => setLibroSeleccionado(null)}>
          <div style={{
            background: 'var(--bg-modal)', borderRadius: '24px 24px 0 0',
            padding: '24px', width: '100%', maxHeight: '80vh', overflowY: 'auto'
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>Detalles del libro</h3>
              <button onClick={() => setLibroSeleccionado(null)} style={{
                background: 'none', border: 'none', color: 'var(--text-secondary)',
                fontSize: '24px', cursor: 'pointer'
              }}>×</button>
            </div>
            <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
              {libroSeleccionado.portada_url ? (
                <img src={libroSeleccionado.portada_url} alt={libroSeleccionado.titulo}
                  style={{ width: '90px', height: '130px', borderRadius: '12px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{
                  width: '90px', height: '130px', borderRadius: '12px',
                  background: 'var(--bg-card)', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px'
                }}>LIB</div>
              )}
              <div>
                <p style={{ fontWeight: 'bold', fontSize: '17px', marginBottom: '6px', lineHeight: '1.3' }}>{libroSeleccionado.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '10px' }}>{libroSeleccionado.autor}</p>
                <span style={{
                  background: 'var(--bg-card)', color: 'var(--accent)',
                  padding: '4px 12px', borderRadius: '20px', fontSize: '12px'
                }}>{libroSeleccionado.genero}</span>
              </div>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6', marginBottom: '20px' }}>
              {libroSeleccionado.descripcion || 'Sin descripción disponible.'}
            </p>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => agregarBiblioteca(libroSeleccionado, 'quiero_leer')} style={estadoBoton(estadosGuardados[libroSeleccionado.id] === 'quiero_leer')}>
                Quiero leer
              </button>
              <button onClick={() => agregarBiblioteca(libroSeleccionado, 'leyendo')} style={estadoBoton(estadosGuardados[libroSeleccionado.id] === 'leyendo')}>
                Leyendo
              </button>
              <button onClick={() => agregarBiblioteca(libroSeleccionado, 'leido')} style={estadoBoton(estadosGuardados[libroSeleccionado.id] === 'leido', true)}>
                Leído
              </button>
            </div>
          </div>
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

const estadoBoton = (activo, primario = false) => ({
  flex: 1,
  background: activo ? 'var(--accent)' : (primario ? 'var(--accent)' : 'var(--bg-card)'),
  color: activo ? 'var(--bg-primary)' : (primario ? 'var(--bg-primary)' : 'var(--text-primary)'),
  border: activo || primario ? 'none' : '1px solid var(--border)',
  borderRadius: '14px',
  padding: '12px',
  fontSize: '13px',
  cursor: 'pointer',
  fontWeight: activo || primario ? 'bold' : '500'
});

export default Search;