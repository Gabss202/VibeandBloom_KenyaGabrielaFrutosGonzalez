import { useState } from 'react';
import axios from 'axios';
import { HiMusicalNote, HiVideoCamera, HiPhoto, HiSparkles } from 'react-icons/hi2';

const API = 'https://fantastic-garbanzo-r47j5ppj6x6xf5w9-8000.app.github.dev';

const Home = () => {
  const [vibeTexto, setVibeTexto] = useState('');
  const [cancion, setCancion] = useState({ nombre: '', artista: '' });
  const [videoUrl, setVideoUrl] = useState('');
  const [imagen, setImagen] = useState(null);
  const [modo, setModo] = useState('texto');
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [mensajeGuardado, setMensajeGuardado] = useState('');

  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const headers = { Authorization: `Bearer ${token}` };

  const detectarVibe = async () => {
    setCargando(true);
    setResultado(null);
    try {
      let res;
      if (modo === 'texto') {
        res = await axios.post(`${API}/vibe/texto`, { texto: vibeTexto }, { headers });
      } else if (modo === 'cancion') {
        res = await axios.post(`${API}/vibe/cancion`, cancion, { headers });
      } else if (modo === 'video') {
        res = await axios.post(`${API}/vibe/video`, { url: videoUrl }, { headers });
      } else if (modo === 'imagen') {
        const formData = new FormData();
        formData.append('imagen', imagen);
        res = await axios.post(`${API}/vibe/imagen`, formData, { headers });
      }
      setResultado(res.data);
    } catch (e) {
      console.error(e);
    }
    setCargando(false);
  };

  const agregarBiblioteca = async (libro, estado) => {
    try {
      await axios.post(`${API}/biblioteca/agregar`, { libro, estado }, { headers });
      setMensajeGuardado(`"${libro.titulo}" agregado como ${estado}`);
      setTimeout(() => setMensajeGuardado(''), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  const modos = [
    { key: 'cancion', icon: <HiMusicalNote size={22} />, label: 'Canción' },
    { key: 'video', icon: <HiVideoCamera size={22} />, label: 'Video' },
    { key: 'imagen', icon: <HiPhoto size={22} />, label: 'Imagen' },
    { key: 'texto', icon: <HiSparkles size={22} />, label: 'Vibe' },
  ];

  return (
    <div style={{ padding: '24px 16px 100px' }}>
      <h2 style={{ fontSize: '26px', marginBottom: '4px' }}>Hola, {username} 👋</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>¿Qué vibes buscas hoy?</p>

      {/* Selector de modo */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        {modos.map(m => (
          <button key={m.key} onClick={() => setModo(m.key)} style={{
            flex: 1, padding: '14px 8px', borderRadius: '16px',
            border: '1px solid var(--border)',
            background: modo === m.key ? 'var(--accent)' : 'var(--bg-card)',
            color: modo === m.key ? 'var(--bg-primary)' : 'var(--text-secondary)',
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            gap: '6px', cursor: 'pointer', fontSize: '11px', fontWeight: '500'
          }}>
            {m.icon}
            {m.label}
          </button>
        ))}
      </div>

      {/* Inputs según modo */}
      <div style={{ background: 'var(--bg-card)', borderRadius: '20px', padding: '20px', marginBottom: '16px' }}>
        <p style={{ color: 'var(--accent)', fontWeight: 'bold', marginBottom: '12px' }}>
          ¿Qué vibe buscas hoy?
        </p>

        {modo === 'texto' && (
          <textarea
            placeholder="Ej: Algo melancólico pero esperanzador, como una tarde lluviosa con café..."
            value={vibeTexto}
            onChange={e => setVibeTexto(e.target.value)}
            rows={4}
            style={{ ...inputStyle, resize: 'none', width: '100%' }}
          />
        )}

        {modo === 'cancion' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input
              placeholder="Nombre de la canción"
              value={cancion.nombre}
              onChange={e => setCancion({ ...cancion, nombre: e.target.value })}
              style={inputStyle}
            />
            <input
              placeholder="Artista (opcional)"
              value={cancion.artista}
              onChange={e => setCancion({ ...cancion, artista: e.target.value })}
              style={inputStyle}
            />
          </div>
        )}

        {modo === 'video' && (
          <input
            placeholder="URL de YouTube"
            value={videoUrl}
            onChange={e => setVideoUrl(e.target.value)}
            style={inputStyle}
          />
        )}

        {modo === 'imagen' && (
          <div>
            <input
              type="file"
              accept="image/*"
              onChange={e => setImagen(e.target.files[0])}
              style={{ color: 'var(--text-primary)', marginBottom: '8px' }}
            />
            {imagen && (
              <img
                src={URL.createObjectURL(imagen)}
                alt="preview"
                style={{ width: '100%', borderRadius: '12px', marginTop: '8px', maxHeight: '200px', objectFit: 'cover' }}
              />
            )}
          </div>
        )}

        <button onClick={detectarVibe} disabled={cargando} style={{
          ...btnStyle, marginTop: '16px', width: '100%',
          opacity: cargando ? 0.7 : 1
        }}>
          {cargando ? 'Analizando vibe...' : 'Obtener recomendaciones ✨'}
        </button>
      </div>

      {/* Mensaje guardado */}
      {mensajeGuardado && (
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--accent)',
          borderRadius: '12px', padding: '12px 16px', marginBottom: '16px',
          color: 'var(--accent)', fontSize: '14px', textAlign: 'center'
        }}>
          ✅ {mensajeGuardado}
        </div>
      )}

      {/* Resultados */}
      {resultado && (
        <div>
          {/* Vibe detectado */}
          <div style={{ background: 'var(--bg-card)', borderRadius: '20px', padding: '20px', marginBottom: '16px' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '4px' }}>Vibe detectado</p>
            <p style={{ fontSize: '22px', fontWeight: 'bold', color: 'var(--accent)', textTransform: 'capitalize', marginBottom: '8px' }}>
              {resultado.vibe?.vibe} ✨
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
              {resultado.vibe?.tags?.map(tag => (
                <span key={tag} style={{
                  background: 'var(--bg-modal)', color: 'var(--text-secondary)',
                  padding: '4px 10px', borderRadius: '20px', fontSize: '12px'
                }}>{tag}</span>
              ))}
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', fontStyle: 'italic' }}>
              {resultado.explicacion?.explicacion}
            </p>
          </div>

          {/* Inferencias */}
          {resultado.recomendaciones?.inferencias?.length > 0 && (
            <div style={{ background: 'var(--bg-card)', borderRadius: '20px', padding: '20px', marginBottom: '16px' }}>
              <p style={{ color: 'var(--accent)', fontWeight: 'bold', marginBottom: '10px' }}>🧠 Razonamiento del sistema</p>
              {resultado.recomendaciones.inferencias.map((inf, i) => (
                <p key={i} style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '6px' }}>
                  • {inf}
                </p>
              ))}
            </div>
          )}

          {/* Libros recomendados */}
          <p style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
            Recomendación para ti
          </p>
          {resultado.recomendaciones?.libros?.map(libro => (
            <div key={libro.id} style={{
              background: 'var(--bg-card)', borderRadius: '20px',
              padding: '16px', marginBottom: '16px',
              display: 'flex', gap: '14px'
            }}>
              {libro.portada_url ? (
                <img src={libro.portada_url} alt={libro.titulo}
                  style={{ width: '80px', height: '110px', borderRadius: '10px', objectFit: 'cover', flexShrink: 0 }} />
              ) : (
                <div style={{
                  width: '80px', height: '110px', borderRadius: '10px',
                  background: 'var(--bg-modal)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  color: 'var(--text-muted)', fontSize: '11px', flexShrink: 0, textAlign: 'center', padding: '4px'
                }}>Sin portada</div>
              )}
              <div style={{ flex: 1 }}>
                <p style={{ fontWeight: 'bold', fontSize: '15px', marginBottom: '4px' }}>{libro.titulo}</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '8px' }}>{libro.autor}</p>
                <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '12px', lineHeight: '1.4' }}>
                  {libro.descripcion?.slice(0, 100)}...
                </p>
                <div style={{ display: 'flex', gap: '8px' }}>
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

const inputStyle = {
  background: 'var(--bg-secondary)', border: '1px solid var(--border)',
  borderRadius: '12px', padding: '12px 14px',
  color: 'var(--text-primary)', fontSize: '14px', outline: 'none', width: '100%'
};

const btnStyle = {
  background: 'var(--accent)', color: 'var(--bg-primary)',
  border: 'none', borderRadius: '12px', padding: '14px',
  fontSize: '15px', fontWeight: 'bold', cursor: 'pointer'
};

const btnSmall = {
  background: 'var(--bg-secondary)', color: 'var(--text-secondary)',
  border: '1px solid var(--border)', borderRadius: '10px',
  padding: '6px 10px', fontSize: '12px', cursor: 'pointer'
};

export default Home;