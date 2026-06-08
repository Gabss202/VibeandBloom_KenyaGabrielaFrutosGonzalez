import { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'https://fantastic-garbanzo-r47j5ppj6x6xf5w9-8000.app.github.dev';

const Library = () => {
  const [biblioteca, setBiblioteca] = useState({ leyendo: [], quiero_leer: [], leidos: [] });
  const [tab, setTab] = useState('leyendo');
  const [modalResena, setModalResena] = useState(null);
  const [resena, setResena] = useState({ calificacion: 5, texto: '' });
  const [mensajeIA, setMensajeIA] = useState('');
  const [cargando, setCargando] = useState(true);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    cargarBiblioteca();
  }, []);

  const cargarBiblioteca = async () => {
    try {
      const res = await axios.get(`${API}/biblioteca`, { headers });
      setBiblioteca(res.data);
    } catch (e) {
      console.error(e);
    }
    setCargando(false);
  };

  const actualizarProgreso = async (libro_id, progreso) => {
    try {
      await axios.post(`${API}/biblioteca/progreso`, { libro_id, progreso }, { headers });
      cargarBiblioteca();
    } catch (e) {
      console.error(e);
    }
  };

  const publicarResena = async () => {
    try {
      const res = await axios.post(`${API}/resenas`, {
        libro_id: modalResena.id,
        calificacion: resena.calificacion,
        texto: resena.texto
      }, { headers });
      setMensajeIA(res.data.respuesta_ia);
      setTimeout(() => {
        setModalResena(null);
        setMensajeIA('');
        setResena({ calificacion: 5, texto: '' });
      }, 4000);
    } catch (e) {
      console.error(e);
    }
  };

  const tabs = ['leyendo', 'quiero_leer', 'leidos'];
  const librosActuales = biblioteca[tab] || [];

  return (
    <div style={{ padding: '24px 16px 100px' }}>
      <h2 style={{ fontSize: '26px', marginBottom: '20px' }}>Mi Biblioteca</h2>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: '20px' }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            flex: 1, padding: '12px 8px', background: 'none',
            border: 'none', borderBottom: tab === t ? '2px solid var(--accent)' : '2px solid transparent',
            color: tab === t ? 'var(--accent)' : 'var(--text-muted)',
            fontSize: '13px', cursor: 'pointer', fontWeight: tab === t ? 'bold' : 'normal',
            textTransform: 'capitalize'
          }}>
            {t === 'quiero_leer' ? 'Quiero leer' : t === 'leidos' ? 'Leídos' : 'Leyendo'}
          </button>
        ))}
      </div>

      {cargando && <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>Cargando...</p>}

      {!cargando && librosActuales.length === 0 && (
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px' }}>
          No tienes libros aquí todavía
        </p>
      )}

      {librosActuales.map(libro => (
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
              color: 'var(--text-muted)', fontSize: '10px', textAlign: 'center', padding: '4px'
            }}>Sin portada</div>
          )}

          <div style={{ flex: 1 }}>
            <p style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '2px' }}>{libro.titulo}</p>
            <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '10px' }}>{libro.autor}</p>

            {tab === 'leyendo' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Progreso</span>
                  <span style={{ color: 'var(--accent)', fontSize: '12px' }}>{libro.progreso}%</span>
                </div>
                <div style={{ background: 'var(--bg-secondary)', borderRadius: '4px', height: '6px', marginBottom: '10px' }}>
                  <div style={{
                    width: `${libro.progreso}%`, height: '100%',
                    background: 'var(--accent)', borderRadius: '4px'
                  }} />
                </div>
                <input
                  type="range" min="0" max="100"
                  value={libro.progreso}
                  onChange={e => actualizarProgreso(libro.id, parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--accent)' }}
                />
              </div>
            )}

            {tab === 'leidos' && (
              <button onClick={() => setModalResena(libro)} style={{
                background: 'var(--accent)', color: 'var(--bg-primary)',
                border: 'none', borderRadius: '10px', padding: '8px 14px',
                fontSize: '13px', cursor: 'pointer', fontWeight: 'bold'
              }}>
                ✍️ Escribir reseña
              </button>
            )}
          </div>
        </div>
      ))}

      {/* Modal Reseña */}
      {modalResena && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
          display: 'flex', alignItems: 'flex-end', zIndex: 200
        }}>
          <div style={{
            background: 'var(--bg-modal)', borderRadius: '24px 24px 0 0',
            padding: '24px', width: '100%', maxHeight: '80vh', overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '20px' }}>Escribe tu reseña</h3>
              <button onClick={() => setModalResena(null)} style={{
                background: 'none', border: 'none', color: 'var(--text-secondary)',
                fontSize: '24px', cursor: 'pointer'
              }}>×</button>
            </div>

            <p style={{ fontWeight: 'bold', marginBottom: '4px' }}>{modalResena.titulo}</p>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>{modalResena.autor}</p>

            {/* Estrellas */}
            <p style={{ marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '13px' }}>Tu calificación</p>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
              {[1, 2, 3, 4, 5].map(n => (
                <span key={n} onClick={() => setResena({ ...resena, calificacion: n })}
                  style={{ fontSize: '28px', cursor: 'pointer', color: n <= resena.calificacion ? 'var(--star)' : 'var(--text-muted)' }}>
                  ★
                </span>
              ))}
            </div>

            <textarea
              placeholder="Comparte tu opinión sobre este libro..."
              value={resena.texto}
              onChange={e => setResena({ ...resena, texto: e.target.value })}
              rows={5}
              maxLength={600}
              style={{
                background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                borderRadius: '12px', padding: '12px', color: 'var(--text-primary)',
                fontSize: '14px', outline: 'none', width: '100%', resize: 'none'
              }}
            />
            <p style={{ color: 'var(--text-muted)', fontSize: '12px', textAlign: 'right', marginBottom: '16px' }}>
              {resena.texto.length}/600
            </p>

            {mensajeIA && (
              <div style={{
                background: 'var(--bg-card)', border: '1px solid var(--accent)',
                borderRadius: '12px', padding: '12px', marginBottom: '16px',
                color: 'var(--accent)', fontSize: '14px', fontStyle: 'italic'
              }}>
                ✨ {mensajeIA}
              </div>
            )}

            <button onClick={publicarResena} style={{
              background: 'var(--accent)', color: 'var(--bg-primary)',
              border: 'none', borderRadius: '12px', padding: '14px',
              fontSize: '15px', fontWeight: 'bold', cursor: 'pointer', width: '100%'
            }}>
              Publicar reseña
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Library;