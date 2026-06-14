import { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { HiMusicalNote, HiVideoCamera, HiPhoto, HiSparkles, HiBookmark, HiBookOpen, HiCheck } from 'react-icons/hi2';
import API from '../config';

const Home = () => {
  const [vibeTexto, setVibeTexto] = useState('');
  const [cancion, setCancion] = useState({ nombre: '', artista: '' });
  const [videoUrl, setVideoUrl] = useState('');
  const [imagen, setImagen] = useState(null);
  const [modo, setModo] = useState('texto');
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [mensajeGuardado, setMensajeGuardado] = useState('');
  const [libroSeleccionado, setLibroSeleccionado] = useState(null);
  const [estadosGuardados, setEstadosGuardados] = useState({});
  const [populares, setPopulares] = useState([]);
  const [popularesCargando, setPopularesCargando] = useState(true);
  const [chatMensajes, setChatMensajes] = useState([
    { role: 'assistant', text: 'Soy Novelia. Puedo recomendarte libros modernos, explicar mis inferencias y ayudarte a elegir tu próxima lectura.' }
  ]);
  const [chatTexto, setChatTexto] = useState('');
  const [chatCargando, setChatCargando] = useState(false);
  const [chatPreferencia, setChatPreferencia] = useState('breve');
  const [chatMostrarBotonesBiblioteca, setChatMostrarBotonesBiblioteca] = useState(true);
  const [reviewModal, setReviewModal] = useState(null);
  const [reviewText, setReviewText] = useState('');
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewMessage, setReviewMessage] = useState('');
  const [chatRecomendaciones, setChatRecomendaciones] = useState([]);

  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const cargarPopulares = useCallback(async () => {
    setPopularesCargando(true);
    try {
      const res = await axios.get(`${API}/libros/populares`, { headers });
      setPopulares(res.data || []);
    } catch (e) { console.error(e); }
    setPopularesCargando(false);
  }, [headers]);

  const cargarEstadosBiblioteca = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/biblioteca`, { headers });
      const estados = {};
      res.data?.leyendo?.forEach(l => { estados[l.id] = 'leyendo'; });
      res.data?.quiero_leer?.forEach(l => { estados[l.id] = 'quiero_leer'; });
      res.data?.leidos?.forEach(l => { estados[l.id] = 'leido'; });
      setEstadosGuardados(estados);
    } catch (e) { console.error(e); }
  }, [headers]);

  useEffect(() => {
    cargarPopulares();
    cargarEstadosBiblioteca();
  }, [cargarPopulares, cargarEstadosBiblioteca]);

  const detectarVibe = async () => {
    setCargando(true);
    setResultado(null);
    try {
      let res;
      if (modo === 'texto') res = await axios.post(`${API}/vibe/texto`, { texto: vibeTexto }, { headers });
      else if (modo === 'cancion') res = await axios.post(`${API}/vibe/cancion`, cancion, { headers });
      else if (modo === 'video') res = await axios.post(`${API}/vibe/video`, { url: videoUrl }, { headers });
      else if (modo === 'imagen') {
        const formData = new FormData();
        formData.append('imagen', imagen);
        res = await axios.post(`${API}/vibe/imagen`, formData, { headers });
      }
      setResultado(res.data);
    } catch (e) { console.error(e); }
    setCargando(false);
  };

  const agregarBiblioteca = async (libro, estado) => {
    try {
      const res = await axios.post(`${API}/biblioteca/agregar`, { libro, estado }, { headers });
      setMensajeGuardado(res.data?.mensaje || `"${libro.titulo}" agregado`);
      await cargarEstadosBiblioteca();
      setLibroSeleccionado(null);
      setTimeout(() => setMensajeGuardado(''), 3000);
    } catch (e) { console.error(e); }
  };

  const abrirModalResena = (libro) => {
    setReviewModal(libro);
    setReviewText('');
    setReviewRating(5);
    setReviewMessage('');
  };

  const publicarResena = async () => {
    if (!reviewModal || !reviewText.trim()) return;
    try {
      const res = await axios.post(`${API}/resenas`, {
        libro_id: reviewModal.id,
        calificacion: reviewRating,
        texto: reviewText.trim()
      }, { headers });
      setReviewMessage(res.data?.respuesta_ia || res.data?.mensaje || 'Reseña publicada.');
      setTimeout(() => { setReviewModal(null); setReviewMessage(''); }, 3500);
    } catch (e) { console.error(e); }
  };

  const enviarChat = async () => {
    if (!chatTexto.trim() || chatCargando) return;
    const mensajeUsuario = chatTexto.trim();
    setChatMensajes(prev => [...prev, { role: 'user', text: mensajeUsuario }]);
    setChatTexto('');
    setChatCargando(true);
    setChatRecomendaciones([]);
    try {
      let payload = mensajeUsuario;
      if (chatPreferencia === 'detallado') payload += ' Por favor, responde con explicaciones más detalladas.';
      else payload += ' Por favor, responde de forma breve y clara.';
      const res = await axios.post(`${API}/chat/libros`, { mensaje: payload }, { headers });
      setChatMensajes(prev => [...prev, { role: 'assistant', text: res.data.respuesta }]);
      setChatRecomendaciones(res.data.recomendaciones || []);
      if (res.data.accion_biblioteca) await cargarEstadosBiblioteca();
    } catch (e) {
      setChatMensajes(prev => [...prev, { role: 'assistant', text: 'No pude responder. Intenta de nuevo.' }]);
    }
    setChatCargando(false);
  };

  const modos = [
    { key: 'cancion', icon: <HiMusicalNote size={20} />, label: 'Canción' },
    { key: 'video', icon: <HiVideoCamera size={20} />, label: 'Video' },
    { key: 'imagen', icon: <HiPhoto size={20} />, label: 'Imagen' },
    { key: 'texto', icon: <HiSparkles size={20} />, label: 'Vibe' },
  ];

  return (
    <div style={{ padding: '24px 16px 100px', maxWidth: '480px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '28px', fontWeight: 'bold' }}>Hola, {username}</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>¿Qué buscas hoy para tu próxima lectura?</p>
      </div>

      {/* Más vendidos */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <p style={{ fontSize: '16px', fontWeight: '700' }}>Más vendidos</p>
          <button onClick={cargarPopulares} style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '13px' }}>Actualizar</button>
        </div>
        {popularesCargando ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Cargando...</p>
        ) : populares.length ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '12px' }}>
            {populares.slice(0, 4).map(libro => (
              <div key={libro.id} onClick={() => setLibroSeleccionado(libro)}
                style={{ background: 'var(--bg-card)', borderRadius: '18px', padding: '14px', border: '1px solid var(--border)', cursor: 'pointer' }}>
                {libro.portada_url ? (
                  <img src={libro.portada_url} alt={libro.titulo}
                    style={{ width: '100%', height: '170px', objectFit: 'cover', borderRadius: '12px', marginBottom: '10px' }} />
                ) : (
                  <div style={{ width: '100%', height: '170px', background: 'var(--bg-modal)', borderRadius: '12px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                    Sin portada
                  </div>
                )}
                <p style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '4px', lineHeight: '1.3' }}>{libro.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginBottom: '10px' }}>{libro.autor}</p>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'quiero_leer'); }}
                    style={btn(estadosGuardados[libro.id] === 'quiero_leer')}>
                    <HiBookmark size={12} /> Quiero leer
                  </button>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'leyendo'); }}
                    style={btn(estadosGuardados[libro.id] === 'leyendo')}>
                    <HiBookOpen size={12} /> Leyendo
                  </button>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'leido'); }}
                    style={btn(estadosGuardados[libro.id] === 'leido')}>
                    <HiCheck size={12} /> Leído
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No hay libros disponibles.</p>
        )}
      </div>

      {/* Selector modo */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        {modos.map(m => (
          <button key={m.key} onClick={() => setModo(m.key)} style={{
            flex: 1, padding: '14px 6px', borderRadius: '18px',
            border: '1px solid var(--border)',
            background: modo === m.key ? 'var(--accent)' : 'var(--bg-card)',
            color: modo === m.key ? 'var(--bg-primary)' : 'var(--text-secondary)',
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            gap: '6px', cursor: 'pointer', fontSize: '11px', fontWeight: '600'
          }}>
            {m.icon}{m.label}
          </button>
        ))}
      </div>

      {/* Card vibe */}
      <div style={{ background: 'var(--bg-card)', borderRadius: '24px', padding: '20px', marginBottom: '20px', border: '1px solid var(--border)' }}>
        <p style={{ color: 'var(--accent)', fontWeight: 'bold', fontSize: '15px', marginBottom: '14px' }}>¿Qué vibe buscas hoy?</p>
        {modo === 'texto' && (
          <textarea placeholder="Ej: Algo melancólico pero esperanzador, como una tarde lluviosa con café..."
            value={vibeTexto} onChange={e => setVibeTexto(e.target.value)} rows={4}
            style={{ ...inputStyle, resize: 'none', width: '100%' }} />
        )}
        {modo === 'cancion' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input placeholder="Nombre de la canción" value={cancion.nombre}
              onChange={e => setCancion({ ...cancion, nombre: e.target.value })} style={inputStyle} />
            <input placeholder="Artista (opcional)" value={cancion.artista}
              onChange={e => setCancion({ ...cancion, artista: e.target.value })} style={inputStyle} />
          </div>
        )}
        {modo === 'video' && (
          <input placeholder="URL de YouTube" value={videoUrl}
            onChange={e => setVideoUrl(e.target.value)} style={inputStyle} />
        )}
        {modo === 'imagen' && (
          <div>
            <input type="file" accept="image/*" onChange={e => setImagen(e.target.files[0])}
              style={{ color: 'var(--text-primary)', marginBottom: '8px', width: '100%' }} />
            {imagen && <img src={URL.createObjectURL(imagen)} alt="preview"
              style={{ width: '100%', borderRadius: '12px', maxHeight: '180px', objectFit: 'cover' }} />}
          </div>
        )}
        <button onClick={detectarVibe} disabled={cargando} style={{
          background: 'var(--accent)', color: 'var(--bg-primary)', border: 'none',
          borderRadius: '14px', padding: '14px', fontSize: '15px', fontWeight: 'bold',
          cursor: 'pointer', width: '100%', marginTop: '14px', opacity: cargando ? 0.7 : 1
        }}>
          {cargando ? 'Analizando...' : 'Obtener recomendaciones'}
        </button>
      </div>

      {mensajeGuardado && (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--accent)', borderRadius: '14px', padding: '12px 16px', marginBottom: '16px', color: 'var(--accent)', fontSize: '14px', textAlign: 'center' }}>
          {mensajeGuardado}
        </div>
      )}

      {/* Chat */}
      <div style={{ background: 'var(--bg-card)', borderRadius: '24px', padding: '18px', marginBottom: '16px', border: '1px solid var(--border)' }}>
        <p style={{ color: 'var(--accent)', fontWeight: 'bold', fontSize: '15px', marginBottom: '8px' }}>Asistente lector</p>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '14px', lineHeight: '1.5' }}>
          Pregúntame por recomendaciones modernas, explicación de reglas, rachas o qué leer según tu estado de ánimo.
        </p>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '14px' }}>
          <button onClick={() => setChatPreferencia('breve')} style={btn(chatPreferencia === 'breve')}>Respuesta breve</button>
          <button onClick={() => setChatPreferencia('detallado')} style={btn(chatPreferencia === 'detallado')}>Respuesta detallada</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '14px' }}>
          {chatMensajes.map((m, i) => (
            <div key={i} style={{
              alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '86%',
              background: m.role === 'user' ? 'var(--accent)' : 'var(--bg-modal)',
              color: m.role === 'user' ? 'var(--bg-primary)' : 'var(--text-primary)',
              borderRadius: '18px', padding: '10px 12px', fontSize: '13px', lineHeight: '1.5'
            }}>{m.text}</div>
          ))}
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input value={chatTexto} onChange={e => setChatTexto(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && enviarChat()}
            placeholder="Ej: recomiéndame algo de dark romance"
            style={{ flex: 1, background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '14px', padding: '12px 14px', color: 'var(--text-primary)', fontSize: '14px', outline: 'none' }} />
          <button onClick={enviarChat} disabled={chatCargando} style={{
            background: 'var(--accent)', color: 'var(--bg-primary)', border: 'none',
            borderRadius: '14px', padding: '12px 16px', fontSize: '14px', fontWeight: 'bold',
            cursor: 'pointer', opacity: chatCargando ? 0.7 : 1
          }}>{chatCargando ? '...' : 'Enviar'}</button>
        </div>
      </div>

      {/* Recomendaciones del chat */}
      {chatRecomendaciones.length > 0 && (
        <div style={{ background: 'var(--bg-card)', borderRadius: '24px', padding: '20px', marginBottom: '16px', border: '1px solid var(--border)' }}>
          <p style={{ color: 'var(--accent)', fontWeight: 'bold', fontSize: '15px', marginBottom: '10px' }}>Recomendaciones</p>
          {chatRecomendaciones.map(libro => (
            <div key={libro.id} style={{ display: 'flex', gap: '14px', padding: '14px', marginBottom: '12px', borderRadius: '18px', background: 'var(--bg-modal)' }}>
              {libro.portada_url ? (
                <img src={libro.portada_url} alt={libro.titulo} style={{ width: '72px', height: '102px', borderRadius: '10px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{ width: '72px', height: '102px', borderRadius: '10px', background: 'var(--bg-secondary)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '11px' }}>Sin portada</div>
              )}
              <div style={{ flex: 1 }}>
                <p style={{ fontWeight: '700', fontSize: '14px', marginBottom: '4px' }}>{libro.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '6px' }}>{libro.autor}</p>
                <p style={{ color: 'var(--text-muted)', fontSize: '11px', marginBottom: '6px' }}>{libro.genero}</p>
                {chatMostrarBotonesBiblioteca && (
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    <button onClick={() => agregarBiblioteca(libro, 'quiero_leer')} style={btn(estadosGuardados[libro.id] === 'quiero_leer')}>
                      <HiBookmark size={12} /> Quiero leer
                    </button>
                    <button onClick={() => agregarBiblioteca(libro, 'leyendo')} style={btn(estadosGuardados[libro.id] === 'leyendo')}>
                      <HiBookOpen size={12} /> Leyendo
                    </button>
                    <button onClick={() => agregarBiblioteca(libro, 'leido')} style={btn(estadosGuardados[libro.id] === 'leido')}>
                      <HiCheck size={12} /> Leído
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Resultado vibe */}
      {resultado && (
        <>
          <div style={{ background: 'var(--bg-card)', borderRadius: '24px', padding: '20px', marginBottom: '16px', border: '1px solid var(--border)' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '1px' }}>Vibe detectado</p>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--accent)', textTransform: 'capitalize', marginBottom: '10px' }}>{resultado.vibe?.vibe}</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
              {resultado.vibe?.tags?.map(tag => (
                <span key={tag} style={{ background: 'var(--bg-modal)', color: 'var(--text-secondary)', padding: '4px 12px', borderRadius: '20px', fontSize: '12px' }}>{tag}</span>
              ))}
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', fontStyle: 'italic', lineHeight: '1.5' }}>{resultado.explicacion?.explicacion}</p>
          </div>

          {resultado.recomendaciones?.inferencias?.length > 0 && (
            <div style={{ background: 'var(--bg-card)', borderRadius: '20px', padding: '16px', marginBottom: '16px', border: '1px solid var(--border)' }}>
              <p style={{ color: 'var(--accent)', fontWeight: 'bold', fontSize: '13px', marginBottom: '10px' }}>Razonamiento del sistema</p>
              {resultado.recomendaciones.inferencias.map((inf, i) => (
                <p key={i} style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '6px' }}>• {inf}</p>
              ))}
            </div>
          )}

          <p style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '14px' }}>Recomendación para ti</p>
          {resultado.recomendaciones?.libros?.map(libro => (
            <div key={libro.id} onClick={() => setLibroSeleccionado(libro)} style={{
              background: 'var(--bg-card)', borderRadius: '20px', padding: '16px', marginBottom: '14px',
              display: 'flex', gap: '14px', cursor: 'pointer', border: '1px solid var(--border)'
            }}>
              {libro.portada_url ? (
                <img src={libro.portada_url} alt={libro.titulo} style={{ width: '75px', height: '110px', borderRadius: '10px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{ width: '75px', height: '110px', borderRadius: '10px', background: 'var(--bg-modal)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '10px' }}>Sin portada</div>
              )}
              <div style={{ flex: 1 }}>
                <p style={{ fontWeight: 'bold', fontSize: '15px', marginBottom: '4px', lineHeight: '1.3' }}>{libro.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '8px' }}>{libro.autor}</p>
                {estadosGuardados[libro.id] && (
                  <p style={{ color: 'var(--accent)', fontSize: '11px', marginBottom: '8px', fontWeight: 'bold' }}>
                    Guardado como: {estadosGuardados[libro.id].replace('_', ' ')}
                  </p>
                )}
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'quiero_leer'); }} style={btn(estadosGuardados[libro.id] === 'quiero_leer')}>
                    <HiBookmark size={12} /> Quiero leer
                  </button>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'leyendo'); }} style={btn(estadosGuardados[libro.id] === 'leyendo')}>
                    <HiBookOpen size={12} /> Leyendo
                  </button>
                  <button onClick={e => { e.stopPropagation(); agregarBiblioteca(libro, 'leido'); }} style={btn(estadosGuardados[libro.id] === 'leido')}>
                    <HiCheck size={12} /> Leído
                  </button>
                </div>
              </div>
            </div>
          ))}
        </>
      )}

      {/* Modal detalles */}
      {libroSeleccionado && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'flex-end', zIndex: 200 }}
          onClick={() => setLibroSeleccionado(null)}>
          <div style={{ background: 'var(--bg-modal)', borderRadius: '24px 24px 0 0', padding: '24px', width: '100%', maxHeight: '80vh', overflowY: 'auto' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>Detalles del libro</h3>
              <button onClick={() => setLibroSeleccionado(null)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', fontSize: '24px', cursor: 'pointer' }}>×</button>
            </div>
            <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
              {libroSeleccionado.portada_url ? (
                <img src={libroSeleccionado.portada_url} alt={libroSeleccionado.titulo} style={{ width: '90px', height: '130px', borderRadius: '12px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{ width: '90px', height: '130px', borderRadius: '12px', background: 'var(--bg-card)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Sin portada</div>
              )}
              <div>
                <p style={{ fontWeight: 'bold', fontSize: '17px', marginBottom: '4px' }}>{libroSeleccionado.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>{libroSeleccionado.autor}</p>
                {estadosGuardados[libroSeleccionado.id] && (
                  <p style={{ color: 'var(--accent)', fontSize: '11px', marginBottom: '8px', fontWeight: 'bold' }}>
                    Guardado como: {estadosGuardados[libroSeleccionado.id].replace('_', ' ')}
                  </p>
                )}
                <span style={{ background: 'var(--bg-card)', color: 'var(--accent)', padding: '4px 10px', borderRadius: '20px', fontSize: '12px' }}>{libroSeleccionado.genero}</span>
              </div>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6', marginBottom: '20px' }}>{libroSeleccionado.descripcion || 'Sin descripción disponible.'}</p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button onClick={() => agregarBiblioteca(libroSeleccionado, 'quiero_leer')} style={btn(estadosGuardados[libroSeleccionado.id] === 'quiero_leer')}>
                <HiBookmark size={14} /> Quiero leer
              </button>
              <button onClick={() => agregarBiblioteca(libroSeleccionado, 'leyendo')} style={btn(estadosGuardados[libroSeleccionado.id] === 'leyendo')}>
                <HiBookOpen size={14} /> Leyendo
              </button>
              <button onClick={() => agregarBiblioteca(libroSeleccionado, 'leido')} style={btn(estadosGuardados[libroSeleccionado.id] === 'leido')}>
                <HiCheck size={14} /> Leído
              </button>
              {estadosGuardados[libroSeleccionado.id] === 'leido' && (
                <button onClick={() => abrirModalResena(libroSeleccionado)} style={btn(false)}>Escribir reseña</button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal reseña */}
      {reviewModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', display: 'flex', alignItems: 'flex-end', zIndex: 220 }}
          onClick={() => setReviewModal(null)}>
          <div style={{ background: 'var(--bg-modal)', borderRadius: '24px 24px 0 0', padding: '24px', width: '100%', maxHeight: '85vh', overflowY: 'auto' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px' }}>Reseña</p>
                <h3 style={{ fontSize: '20px', fontWeight: 'bold' }}>{reviewModal.titulo}</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{reviewModal.autor}</p>
              </div>
              <button onClick={() => setReviewModal(null)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', fontSize: '24px', cursor: 'pointer' }}>×</button>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '6px' }}>Calificación</p>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '18px' }}>
              {[1, 2, 3, 4, 5].map(n => (
                <span key={n} onClick={() => setReviewRating(n)}
                  style={{ fontSize: '30px', cursor: 'pointer', color: n <= reviewRating ? 'var(--accent)' : 'var(--text-muted)' }}>★</span>
              ))}
            </div>
            <textarea placeholder="Escribe tu reseña aquí..." value={reviewText}
              onChange={e => setReviewText(e.target.value)} rows={5}
              style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '14px', padding: '14px', color: 'var(--text-primary)', fontSize: '14px', outline: 'none', width: '100%', resize: 'vertical', lineHeight: '1.5' }} />
            <p style={{ color: 'var(--text-muted)', fontSize: '12px', textAlign: 'right', margin: '8px 0 18px' }}>{reviewText.length}/500</p>
            {reviewMessage && (
              <div style={{ background: 'var(--bg-card)', border: '1px solid var(--accent)', borderRadius: '14px', padding: '14px', marginBottom: '16px', color: 'var(--accent)', fontSize: '14px', lineHeight: '1.5' }}>
                {reviewMessage}
              </div>
            )}
            <button onClick={publicarResena} style={{ background: 'var(--accent)', color: 'var(--bg-primary)', border: 'none', borderRadius: '14px', padding: '16px', fontSize: '15px', fontWeight: 'bold', cursor: 'pointer', width: '100%' }}>
              Publicar reseña
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const inputStyle = {
  background: 'var(--bg-secondary)', border: '1px solid var(--border)',
  borderRadius: '12px', padding: '12px 14px',
  color: 'var(--text-primary)', fontSize: '14px', outline: 'none', width: '100%'
};

const btn = (activo) => ({
  display: 'flex', alignItems: 'center', gap: '4px',
  flex: 1, background: activo ? 'var(--accent)' : 'var(--bg-secondary)',
  color: activo ? 'var(--bg-primary)' : 'var(--text-secondary)',
  border: '1px solid var(--border)', borderRadius: '10px',
  padding: '8px 10px', fontSize: '12px', cursor: 'pointer',
  fontWeight: activo ? 'bold' : '400'
});

export default Home;