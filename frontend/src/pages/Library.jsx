import { useState, useEffect } from 'react';
import axios from 'axios';
import API from '../config';

const Library = () => {
  const [biblioteca, setBiblioteca] = useState({ leyendo: [], quiero_leer: [], leidos: [] });
  const [tab, setTab] = useState('leyendo');
  const [modalResena, setModalResena] = useState(null);
  const [resena, setResena] = useState({ calificacion: 5, texto: '' });
  const [mensajeIA, setMensajeIA] = useState('');
  const [mensajeSistema, setMensajeSistema] = useState('');
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
      const res = await axios.post(`${API}/biblioteca/progreso`, { libro_id, progreso }, { headers });
      setMensajeSistema(res.data?.inferencia || res.data?.mensaje || '');
      setTimeout(() => setMensajeSistema(''), 3500);
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
      setMensajeSistema(res.data.mensaje || 'Reseña registrada correctamente');
      setTimeout(() => {
        setModalResena(null);
        setMensajeIA('');
        setMensajeSistema('');
        setResena({ calificacion: 5, texto: '' });
        cargarBiblioteca();
      }, 4000);
    } catch (e) {
      console.error(e);
    }
  };

  const tabs = [
    { key: 'leyendo', label: 'Leyendo' },
    { key: 'quiero_leer', label: 'Quiero leer' },
    { key: 'leidos', label: 'Leídos' },
  ];

  const librosActuales = biblioteca[tab] || [];

  return (
    <div style={{ padding: '24px 16px 100px', maxWidth: '480px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '20px' }}>Mi Biblioteca</h2>

      {mensajeSistema && (
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--accent)',
          borderRadius: '14px', padding: '12px 14px', marginBottom: '16px',
          color: 'var(--accent)', fontSize: '14px', lineHeight: '1.5'
        }}>
          🧠 {mensajeSistema}
        </div>
      )}

      {/* Tabs */}
      <div style={{
        display: 'flex', borderBottom: '1px solid var(--border)',
        marginBottom: '22px', gap: '4px'
      }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)} style={{
            flex: 1, padding: '12px 6px', background: 'none', border: 'none',
            borderBottom: tab === t.key ? '2px solid var(--accent)' : '2px solid transparent',
            color: tab === t.key ? 'var(--accent)' : 'var(--text-muted)',
            fontSize: '13px', cursor: 'pointer',
            fontWeight: tab === t.key ? 'bold' : 'normal',
            transition: 'all 0.2s'
          }}>
            {t.label}
            <span style={{
              marginLeft: '6px', background: tab === t.key ? 'var(--accent)' : 'var(--bg-card)',
              color: tab === t.key ? 'var(--bg-primary)' : 'var(--text-muted)',
              borderRadius: '10px', padding: '1px 7px', fontSize: '11px'
            }}>
              {biblioteca[t.key]?.length || 0}
            </span>
          </button>
        ))}
      </div>

      {cargando && (
        <div style={{ textAlign: 'center', marginTop: '60px' }}>
          <p style={{ fontSize: '32px', marginBottom: '12px' }}>📚</p>
          <p style={{ color: 'var(--text-muted)' }}>Cargando biblioteca...</p>
        </div>
      )}

      {!cargando && librosActuales.length === 0 && (
        <div style={{ textAlign: 'center', marginTop: '60px' }}>
          <p style={{ fontSize: '48px', marginBottom: '16px' }}>
            {tab === 'leyendo' ? '📖' : tab === 'quiero_leer' ? '🔖' : '✅'}
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '15px' }}>
            {tab === 'leyendo' ? 'No estás leyendo nada aún' :
             tab === 'quiero_leer' ? 'Tu lista de deseos está vacía' :
             'Aún no has marcado libros como leídos'}
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '8px' }}>
            Busca libros y agrégalos aquí
          </p>
        </div>
      )}

      {librosActuales.map(libro => (
        <div key={libro.id} style={{
          background: 'var(--bg-card)', borderRadius: '18px',
          padding: '14px', marginBottom: '14px',
          display: 'flex', gap: '14px',
          border: '1px solid var(--border)'
        }}>
          {libro.portada_url ? (
            <img src={libro.portada_url} alt={libro.titulo}
              style={{ width: '70px', height: '100px', borderRadius: '10px', objectFit: 'cover', flexShrink: 0 }} />
          ) : (
            <div style={{
              width: '70px', height: '100px', borderRadius: '10px',
              background: 'var(--bg-modal)', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px'
            }}>📚</div>
          )}

          <div style={{ flex: 1 }}>
            <p style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '2px', lineHeight: '1.3' }}>
              {libro.titulo}
            </p>
            <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '10px' }}>
              {libro.autor}
            </p>

            {tab === 'leyendo' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Progreso</span>
                  <span style={{ color: 'var(--accent)', fontSize: '12px', fontWeight: 'bold' }}>
                    {libro.progreso}%
                  </span>
                </div>
                <div style={{
                  background: 'var(--bg-secondary)', borderRadius: '6px',
                  height: '6px', marginBottom: '10px', overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${libro.progreso}%`, height: '100%',
                    background: 'var(--accent)', borderRadius: '6px',
                    transition: 'width 0.3s'
                  }} />
                </div>
                <input
                  type="range" min="0" max="100"
                  value={libro.progreso}
                  onChange={e => actualizarProgreso(libro.id, parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--accent)', cursor: 'pointer' }}
                />
              </div>
            )}

            {tab === 'quiero_leer' && (
              <p style={{ color: 'var(--text-muted)', fontSize: '12px', fontStyle: 'italic' }}>
                En tu lista de deseos
              </p>
            )}

            {tab === 'leidos' && (
              <button onClick={() => setModalResena(libro)} style={{
                background: 'var(--accent)', color: 'var(--bg-primary)',
                border: 'none', borderRadius: '10px', padding: '8px 14px',
                fontSize: '12px', cursor: 'pointer', fontWeight: 'bold'
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
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)',
          display: 'flex', alignItems: 'flex-end', zIndex: 200
        }}>
          <div style={{
            background: 'var(--bg-modal)', borderRadius: '24px 24px 0 0',
            padding: '24px', width: '100%', maxHeight: '85vh', overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: 'bold' }}>Escribe tu reseña</h3>
              <button onClick={() => setModalResena(null)} style={{
                background: 'none', border: 'none',
                color: 'var(--text-secondary)', fontSize: '26px', cursor: 'pointer'
              }}>×</button>
            </div>

            <div style={{ display: 'flex', gap: '14px', marginBottom: '20px' }}>
              {modalResena.portada_url ? (
                <img src={modalResena.portada_url} alt={modalResena.titulo}
                  style={{ width: '70px', height: '100px', borderRadius: '10px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{
                  width: '70px', height: '100px', borderRadius: '10px',
                  background: 'var(--bg-card)', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px'
                }}>📚</div>
              )}
              <div>
                <p style={{ fontWeight: 'bold', fontSize: '15px', marginBottom: '4px' }}>{modalResena.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{modalResena.autor}</p>
              </div>
            </div>

            {/* Estrellas */}
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '10px' }}>
              Tu calificación
            </p>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '18px' }}>
              {[1, 2, 3, 4, 5].map(n => (
                <span key={n} onClick={() => setResena({ ...resena, calificacion: n })}
                  style={{
                    fontSize: '32px', cursor: 'pointer',
                    color: n <= resena.calificacion ? 'var(--star)' : 'var(--text-muted)',
                    transition: 'color 0.1s'
                  }}>★</span>
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
                borderRadius: '14px', padding: '14px',
                color: 'var(--text-primary)', fontSize: '14px',
                outline: 'none', width: '100%', resize: 'none', lineHeight: '1.5'
              }}
            />
            <p style={{
              color: 'var(--text-muted)', fontSize: '12px',
              textAlign: 'right', margin: '6px 0 16px'
            }}>
              {resena.texto.length}/600
            </p>

            {mensajeIA && (
              <div style={{
                background: 'var(--bg-card)', border: '1px solid var(--accent)',
                borderRadius: '14px', padding: '14px', marginBottom: '16px',
                color: 'var(--accent)', fontSize: '14px', fontStyle: 'italic',
                lineHeight: '1.5'
              }}>
                ✨ {mensajeIA}
              </div>
            )}

            <button onClick={publicarResena} style={{
              background: 'var(--accent)', color: 'var(--bg-primary)',
              border: 'none', borderRadius: '14px', padding: '16px',
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
