import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import API from '../config';

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

  const vibeEmoji = {
    melancolico: '🌧️', romantico: '🌹', misterioso: '🌙',
    cozy: '☕', aventurero: '🗺️', oscuro: '🖤', esperanzador: '🌟'
  };

  const retosCompletados = resumen?.retos?.filter(reto => reto.progreso >= 100).length || 0;
  const formatearFecha = (fecha) => {
    if (!fecha) return 'Sin datos';
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const totalProgresoRetos = resumen?.retos?.length
    ? Math.round(resumen.retos.reduce((acumulado, reto) => acumulado + reto.progreso, 0) / resumen.retos.length)
    : 0;

  return (
    <div style={{ padding: '24px 16px 100px', maxWidth: '480px', margin: '0 auto' }}>

      {/* Header perfil */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '68px', height: '68px', borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--accent), #8B6914)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '26px', color: 'var(--bg-primary)', fontWeight: 'bold',
            flexShrink: 0
          }}>
            {username?.charAt(0).toUpperCase()}
          </div>
          <div>
            <p style={{ fontSize: '20px', fontWeight: 'bold' }}>{username}</p>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>@{username?.toLowerCase()}</p>
          </div>
        </div>
      </div>

      {cargando && (
        <div style={{ textAlign: 'center', marginTop: '60px' }}>
          <p style={{ fontSize: '32px', marginBottom: '12px' }}>📚</p>
          <p style={{ color: 'var(--text-muted)' }}>Cargando tu perfil...</p>
        </div>
      )}

      {resumen && (
        <>
          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '18px',
            border: '1px solid var(--border)'
          }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Vista rápida
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
              {[
                { label: 'Racha', valor: `${resumen.estadisticas.racha_lectura} días`, emoji: '🔥' },
                { label: 'Actividad', valor: resumen.estadisticas.actividad_total, emoji: '📈' },
                { label: 'Última vez', valor: formatearFecha(resumen.ultima_actividad), emoji: '🕒' },
              ].map(item => (
                <div key={item.label} style={{
                  background: 'var(--bg-modal)', borderRadius: '14px',
                  padding: '12px', textAlign: 'center'
                }}>
                  <p style={{ fontSize: '18px', marginBottom: '6px' }}>{item.emoji}</p>
                  <p style={{ fontSize: '15px', fontWeight: 'bold', color: 'var(--accent)', marginBottom: '2px', lineHeight: '1.2' }}>
                    {item.valor}
                  </p>
                  <p style={{ color: 'var(--text-muted)', fontSize: '11px' }}>{item.label}</p>
                </div>
              ))}
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: '12px', lineHeight: '1.5' }}>
              {retosCompletados} de {resumen.retos.length} retos están completados y tu vibe favorito es <span style={{ color: 'var(--accent)', fontWeight: 'bold', textTransform: 'capitalize' }}>{resumen.vibe_favorito}</span>.
            </p>
          </div>

          {/* Stats grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
            {[
              { label: 'Libros leídos', valor: resumen.estadisticas.libros_leidos, emoji: '📚' },
              { label: 'Calificación promedio', valor: resumen.estadisticas.rating_promedio || '—', emoji: '⭐' },
              { label: 'Leyendo ahora', valor: resumen.estadisticas.leyendo_ahora, emoji: '📖' },
              { label: 'Por leer', valor: resumen.estadisticas.quiero_leer, emoji: '🔖' },
              { label: 'Racha', valor: resumen.estadisticas.racha_lectura, emoji: '🔥' },
              { label: 'Días activos 30', valor: resumen.estadisticas.dias_activos_30, emoji: '📅' },
              { label: 'Nivel lector', valor: resumen.nivel_lector || 'Inicial', emoji: '🧭' },
              { label: 'Progreso semanal', valor: `${resumen.estadisticas.progreso_semanal || 0}%`, emoji: '⏳' },
            ].map(stat => (
              <div key={stat.label} style={{
                background: 'var(--bg-card)', borderRadius: '18px',
                padding: '18px', textAlign: 'center',
                border: '1px solid var(--border)'
              }}>
                <p style={{ fontSize: '26px', marginBottom: '6px' }}>{stat.emoji}</p>
                <p style={{ fontSize: '26px', fontWeight: 'bold', color: 'var(--accent)', marginBottom: '4px' }}>
                  {stat.valor}
                </p>
                <p style={{ color: 'var(--text-muted)', fontSize: '11px' }}>{stat.label}</p>
              </div>
            ))}
          </div>

          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '14px',
            border: '1px solid var(--border)'
          }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Racha de lectura
            </p>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
              <div>
                <p style={{ fontSize: '28px', fontWeight: 'bold', color: 'var(--accent)' }}>{resumen.estadisticas.racha_lectura} días</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Actividad lectora reciente y consistente
                </p>
              </div>
              <div style={{
                width: '72px', height: '72px', borderRadius: '50%',
                border: '6px solid var(--bg-modal)',
                borderTopColor: 'var(--accent)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'var(--accent)', fontWeight: 'bold'
              }}>
                {totalProgresoRetos}%
              </div>
            </div>
          </div>

          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '14px',
            border: '1px solid var(--border)'
          }}>
            <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)', fontSize: '14px' }}>
              🏆 Retos de lectura
            </p>
            {resumen.retos.map((reto, indice) => (
              <div key={reto.titulo} style={{ marginBottom: indice < resumen.retos.length - 1 ? '14px' : '0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <p style={{ fontSize: '13px', fontWeight: '600' }}>{reto.titulo}</p>
                  <p style={{ color: 'var(--accent)', fontSize: '12px', fontWeight: 'bold' }}>{reto.progreso}%</p>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '8px', lineHeight: '1.4' }}>{reto.descripcion}</p>
                <div style={{ background: 'var(--bg-modal)', borderRadius: '999px', height: '7px', overflow: 'hidden' }}>
                  <div style={{ width: `${reto.progreso}%`, height: '100%', background: 'var(--accent)' }} />
                </div>
              </div>
            ))}
          </div>

          {resumen.actividad_reciente?.length > 0 && (
            <div style={{
              background: 'var(--bg-card)', borderRadius: '18px',
              padding: '18px', marginBottom: '14px',
              border: '1px solid var(--border)'
            }}>
              <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)', fontSize: '14px' }}>
                ⚡ Actividad reciente
              </p>
              {resumen.actividad_reciente.map((actividad, index) => (
                <div key={`${actividad.fecha}-${index}`} style={{ marginBottom: index < resumen.actividad_reciente.length - 1 ? '10px' : '0' }}>
                  <p style={{ fontSize: '13px', fontWeight: '600', marginBottom: '2px' }}>{actividad.tipo}</p>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '12px', lineHeight: '1.4' }}>{actividad.detalle}</p>
                </div>
              ))}
            </div>
          )}

          {/* Vibe favorito */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '14px',
            border: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between'
          }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Tu vibe favorito
              </p>
              <p style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent)', textTransform: 'capitalize' }}>
                {resumen.vibe_favorito}
              </p>
            </div>
            <span style={{ fontSize: '36px' }}>
              {vibeEmoji[resumen.vibe_favorito] || '✨'}
            </span>
          </div>

          {/* Análisis perfil */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '14px',
            border: '1px solid var(--border)'
          }}>
            <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)', fontSize: '14px' }}>
              🧠 Análisis de tu perfil lector
            </p>
            {resumen.inferencias_perfil.map((inf, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'flex-start', gap: '10px', marginBottom: '10px'
              }}>
                <span style={{
                  width: '6px', height: '6px', borderRadius: '50%',
                  background: 'var(--accent)', flexShrink: 0, marginTop: '6px'
                }} />
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '1.5' }}>{inf}</p>
              </div>
            ))}
          </div>

          {/* Reseñas */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '24px',
            border: '1px solid var(--border)',
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

          {/* Configuración */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            border: '1px solid var(--border)', marginBottom: '16px', overflow: 'hidden'
          }}>
            {[
              { label: 'Actividad reciente', emoji: '📊' },
              { label: 'Estadísticas', emoji: '📈' },
              { label: 'Retos de lectura', emoji: '🏆' },
            ].map((item, i) => (
              <div key={item.label} style={{
                padding: '16px 18px', display: 'flex', alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: i < 2 ? '1px solid var(--border)' : 'none',
                cursor: 'pointer'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '18px' }}>{item.emoji}</span>
                  <p style={{ fontSize: '14px' }}>{item.label}</p>
                </div>
                <span style={{ color: 'var(--text-muted)' }}>›</span>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Cerrar sesión */}
      <button onClick={cerrarSesion} style={{
        width: '100%', background: 'none',
        border: '1px solid #c0635a', borderRadius: '14px',
        padding: '14px', color: '#c0635a',
        fontSize: '15px', cursor: 'pointer', fontWeight: 'bold'
      }}>
        Cerrar sesión
      </button>
    </div>
  );
};

export default Profile;