import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API = 'https://fantastic-garbanzo-r47j5ppj6x6xf5w9-8000.app.github.dev';

const Profile = () => {
  const [resumen, setResumen] = useState(null);
  const [cargando, setCargando] = useState(true);
  const navigate = useNavigate();

  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    cargarResumen();
  }, []);

  const cargarResumen = async () => {
    try {
      const res = await axios.get(`${API}/perfil/resumen`, { headers });
      setResumen(res.data);
    } catch (e) {
      console.error(e);
    }
    setCargando(false);
  };

  const cerrarSesion = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <div style={{ padding: '24px 16px 100px' }}>
      {/* Header perfil */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '28px' }}>
        <div style={{
          width: '72px', height: '72px', borderRadius: '50%',
          background: 'var(--accent)', display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          fontSize: '28px', color: 'var(--bg-primary)', fontWeight: 'bold'
        }}>
          {username?.charAt(0).toUpperCase()}
        </div>
        <div>
          <p style={{ fontSize: '20px', fontWeight: 'bold' }}>{username}</p>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>@{username}</p>
        </div>
      </div>

      {cargando && <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>Cargando...</p>}

      {resumen && (
        <>
          {/* Estadísticas */}
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr',
            gap: '12px', marginBottom: '24px'
          }}>
            {[
              { label: 'Libros leídos', valor: resumen.estadisticas.libros_leidos, emoji: '📚' },
              { label: 'Calificación promedio', valor: resumen.estadisticas.rating_promedio || '—', emoji: '⭐' },
              { label: 'Leyendo ahora', valor: resumen.estadisticas.leyendo_ahora, emoji: '📖' },
              { label: 'Por leer', valor: resumen.estadisticas.quiero_leer, emoji: '🔖' },
            ].map(stat => (
              <div key={stat.label} style={{
                background: 'var(--bg-card)', borderRadius: '16px',
                padding: '16px', textAlign: 'center'
              }}>
                <p style={{ fontSize: '28px', marginBottom: '4px' }}>{stat.emoji}</p>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--accent)' }}>{stat.valor}</p>
                <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{stat.label}</p>
              </div>
            ))}
          </div>

          {/* Vibe favorito */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '16px',
            padding: '16px', marginBottom: '16px'
          }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '4px' }}>Tu vibe favorito</p>
            <p style={{ fontSize: '20px', fontWeight: 'bold', color: 'var(--accent)', textTransform: 'capitalize' }}>
              ✨ {resumen.vibe_favorito}
            </p>
          </div>

          {/* Inferencias del perfil */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '16px',
            padding: '16px', marginBottom: '16px'
          }}>
            <p style={{ fontWeight: 'bold', marginBottom: '12px', color: 'var(--accent)' }}>
              🧠 Análisis de tu perfil lector
            </p>
            {resumen.inferencias_perfil.map((inf, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'flex-start', gap: '8px',
                marginBottom: '8px'
              }}>
                <span style={{ color: 'var(--accent)', marginTop: '2px' }}>•</span>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '1.5' }}>{inf}</p>
              </div>
            ))}
          </div>

          {/* Total reseñas */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '16px',
            padding: '16px', marginBottom: '24px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between'
          }}>
            <div>
              <p style={{ fontWeight: 'bold', marginBottom: '4px' }}>Mis reseñas</p>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                {resumen.estadisticas.total_reseñas} reseñas publicadas
              </p>
            </div>
            <span style={{ fontSize: '32px' }}>✍️</span>
          </div>
        </>
      )}

      {/* Cerrar sesión */}
      <button onClick={cerrarSesion} style={{
        width: '100%', background: 'none',
        border: '1px solid #e07070', borderRadius: '12px',
        padding: '14px', color: '#e07070',
        fontSize: '15px', cursor: 'pointer', fontWeight: 'bold'
      }}>
        Cerrar sesión
      </button>
    </div>
  );
};

export default Profile;