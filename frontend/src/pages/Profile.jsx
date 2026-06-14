import { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import API from '../config';

const Profile = () => {
  const [resumen, setResumen] = useState(null);
  const [retos, setRetos] = useState([]);
  const [resenas, setResenas] = useState([]);
  const [seccionActiva, setSeccionActiva] = useState('actividad');
  const [nuevoReto, setNuevoReto] = useState({ titulo: '', descripcion: '', progreso: 0 });
  const [editando, setEditando] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [cargandoRetos, setCargandoRetos] = useState(true);
  const [cargandoResenas, setCargandoResenas] = useState(false);
  const navigate = useNavigate();

  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const cargarResumen = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/perfil/resumen`, { headers });
      setResumen(res.data);
    } catch (e) {
      console.error(e);
    }
    setCargando(false);
  }, [headers]);

  const cargarRetos = useCallback(async () => {
    setCargandoRetos(true);
    try {
      const res = await axios.get(`${API}/retos`, { headers });
      setRetos(res.data || []);
    } catch (e) {
      console.error(e);
    }
    setCargandoRetos(false);
  }, [headers]);

  const cargarResenas = useCallback(async () => {
    setCargandoResenas(true);
    try {
      const res = await axios.get(`${API}/resenas`, { headers });
      setResenas(res.data || []);
    } catch (e) {
      console.error(e);
    }
    setCargandoResenas(false);
  }, [headers]);

  const mostrarResenas = async () => {
    await cargarResenas();
    setSeccionActiva('resenas');
  };

  useEffect(() => {
    cargarResumen();
    cargarRetos();
  }, [cargarResumen, cargarRetos]);

  const guardarReto = async () => {
    if (!nuevoReto.titulo.trim() || !nuevoReto.descripcion.trim()) return;
    try {
      if (editando) {
        await axios.patch(`${API}/retos/${editando.id}`, nuevoReto, { headers });
      } else {
        await axios.post(`${API}/retos`, nuevoReto, { headers });
      }
      setNuevoReto({ titulo: '', descripcion: '', progreso: 0 });
      setEditando(null);
      cargarRetos();
      cargarResumen();
    } catch (e) {
      console.error(e);
    }
  };

  const editarReto = (reto) => {
    setEditando(reto);
    setNuevoReto({ titulo: reto.titulo, descripcion: reto.descripcion, progreso: reto.progreso });
  };

  const eliminarReto = async (id) => {
    try {
      await axios.delete(`${API}/retos/${id}`, { headers });
      cargarRetos();
      cargarResumen();
    } catch (e) {
      console.error(e);
    }
  };

  const cerrarSesion = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  const vibeEmoji = {
    melancolico: 'Mel', romantico: 'Rom', misterioso: 'Mis',
    cozy: 'Cozy', aventurero: 'Aven', oscuro: 'Osc', esperanzador: 'Esp'
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
          <p style={{ fontSize: '32px', marginBottom: '12px' }}>Perfil</p>
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
                { label: 'Racha', valor: `${resumen.estadisticas.racha_lectura} días`, emoji: '' },
                { label: 'Actividad', valor: resumen.estadisticas.actividad_total, emoji: '' },
                { label: 'Última vez', valor: formatearFecha(resumen.ultima_actividad), emoji: '' },
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
              { label: 'Libros leídos', valor: resumen.estadisticas.libros_leidos, emoji: '' },
              { label: 'Calificación promedio', valor: resumen.estadisticas.rating_promedio || '—', emoji: '' },
              { label: 'Leyendo ahora', valor: resumen.estadisticas.leyendo_ahora, emoji: '' },
              { label: 'Por leer', valor: resumen.estadisticas.quiero_leer, emoji: '' },
              { label: 'Racha', valor: resumen.estadisticas.racha_lectura, emoji: '' },
              { label: 'Días activos 30', valor: resumen.estadisticas.dias_activos_30, emoji: '' },
              { label: 'Nivel lector', valor: resumen.nivel_lector || 'Inicial', emoji: '' },
              { label: 'Progreso semanal', valor: `${resumen.estadisticas.progreso_semanal || 0}%`, emoji: '' },
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
              Retos de lectura
            </p>
            {(resumen.retos || []).map((reto, indice) => (
              <div key={reto.titulo} style={{ marginBottom: indice < (resumen.retos || []).length - 1 ? '14px' : '0' }}>
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

          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '14px',
            border: '1px solid var(--border)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <p style={{ fontWeight: 'bold', fontSize: '14px' }}>Gestionar retos</p>
              <button onClick={() => { setEditando(null); setNuevoReto({ titulo: '', descripcion: '', progreso: 0 }); }} style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '12px' }}>
                Nuevo reto
              </button>
            </div>
            {cargandoRetos ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Cargando retos...</p>
            ) : retos.length ? (
              retos.map(reto => (
                <div key={reto.id} style={{ marginBottom: '12px', padding: '12px', background: 'var(--bg-modal)', borderRadius: '14px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', marginBottom: '8px' }}>
                    <div>
                      <p style={{ fontSize: '13px', fontWeight: '600' }}>{reto.titulo}</p>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>{reto.descripcion}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ fontSize: '12px', fontWeight: '700', color: 'var(--accent)' }}>{reto.progreso}%</p>
                      <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                        <button onClick={() => editarReto(reto)} style={actionButton}>Editar</button>
                        <button onClick={() => eliminarReto(reto.id)} style={deleteButton}>Borrar</button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Aún no tienes retos personalizados. Agrégalos aquí.</p>
            )}

            <div style={{ marginTop: '18px', display: 'grid', gap: '10px' }}>
              <input
                placeholder="Título del reto"
                value={nuevoReto.titulo}
                onChange={e => setNuevoReto({ ...nuevoReto, titulo: e.target.value })}
                style={inputStyle}
              />
              <textarea
                placeholder="Descripción del reto"
                rows={3}
                value={nuevoReto.descripcion}
                onChange={e => setNuevoReto({ ...nuevoReto, descripcion: e.target.value })}
                style={{ ...inputStyle, resize: 'vertical' }}
              />
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={nuevoReto.progreso}
                  onChange={e => setNuevoReto({ ...nuevoReto, progreso: Number(e.target.value) })}
                  style={{ ...inputStyle, width: '100px' }}
                />
                <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Progreso %</span>
              </div>
              <button onClick={guardarReto} style={btnStyle}>
                {editando ? 'Guardar cambios' : 'Agregar reto'}
              </button>
            </div>
          </div>

          {resumen.actividad_reciente?.length > 0 && (
            <div style={{
              background: 'var(--bg-card)', borderRadius: '18px',
              padding: '18px', marginBottom: '14px',
              border: '1px solid var(--border)'
            }}>
              <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)', fontSize: '14px' }}>
                Actividad reciente
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
              {vibeEmoji[resumen.vibe_favorito] || 'Vibe'}
            </span>
          </div>

          {/* Análisis perfil */}
          <div style={{
            background: 'var(--bg-card)', borderRadius: '18px',
            padding: '18px', marginBottom: '14px',
            border: '1px solid var(--border)'
          }}>
            <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)', fontSize: '14px' }}>
              Análisis de tu perfil lector
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
            padding: '18px', marginBottom: '14px',
            border: '1px solid var(--border)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', alignItems: 'center' }}>
              <div>
                <p style={{ fontWeight: 'bold', marginBottom: '4px' }}>Mis reseñas</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  {resumen.estadisticas.total_reseñas} reseñas publicadas
                </p>
              </div>
              <button onClick={mostrarResenas} style={{
                background: 'var(--accent)', color: 'var(--bg-primary)',
                border: 'none', borderRadius: '12px', padding: '10px 14px',
                fontSize: '12px', cursor: 'pointer', fontWeight: 'bold'
              }}>
                Ver reseñas
              </button>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '1.5' }}>
              Revisa tus reseñas y disfruta de una experiencia completa con libros ya leídos.
            </p>
          </div>

          {/* Configuración */}
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '18px'
          }}>
            {[
              { key: 'actividad', label: 'Actividad reciente' },
              { key: 'estadisticas', label: 'Estadísticas' },
              { key: 'retos', label: 'Retos de lectura' },
            ].map(item => (
              <button key={item.key} onClick={() => setSeccionActiva(item.key)} style={{
                background: seccionActiva === item.key ? 'var(--accent)' : 'var(--bg-card)',
                color: seccionActiva === item.key ? 'var(--bg-primary)' : 'var(--text-primary)',
                border: '1px solid var(--border)', borderRadius: '16px',
                padding: '14px 10px', fontSize: '12px', cursor: 'pointer', fontWeight: '700'
              }}>
                {item.label}
              </button>
            ))}
          </div>
          {seccionActiva === 'actividad' && (
            <div style={{
              background: 'var(--bg-card)', borderRadius: '18px', padding: '18px',
              border: '1px solid var(--border)', marginBottom: '14px'
            }}>
              <p style={{ fontWeight: 'bold', marginBottom: '12px', color: 'var(--accent)' }}>Actividad reciente</p>
              {resumen.actividad_reciente?.length ? (
                resumen.actividad_reciente.map((actividad, index) => (
                  <div key={`${actividad.fecha}-${index}`} style={{ marginBottom: index < resumen.actividad_reciente.length - 1 ? '10px' : '0' }}>
                    <p style={{ fontSize: '13px', fontWeight: '600', marginBottom: '2px' }}>{actividad.tipo}</p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '12px', lineHeight: '1.4' }}>{actividad.detalle}</p>
                  </div>
                ))
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Aún no hay actividad registrada.</p>
              )}
            </div>
          )}
          {seccionActiva === 'estadisticas' && (
            <div style={{
              background: 'var(--bg-card)', borderRadius: '18px', padding: '18px',
              border: '1px solid var(--border)', marginBottom: '14px'
            }}>
              <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)' }}>Estadísticas</p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                {[
                  { label: 'Libros leídos', value: resumen.estadisticas.libros_leidos },
                  { label: 'Leyendo ahora', value: resumen.estadisticas.leyendo_ahora },
                  { label: 'Por leer', value: resumen.estadisticas.quiero_leer },
                  { label: 'Racha', value: `${resumen.estadisticas.racha_lectura} días` },
                  { label: 'Calif. promedio', value: resumen.estadisticas.rating_promedio || '—' },
                  { label: 'Progreso sem.', value: `${resumen.estadisticas.progreso_semanal}%` },
                ].map(item => (
                  <div key={item.label} style={{ background: 'var(--bg-modal)', borderRadius: '14px', padding: '14px' }}>
                    <p style={{ fontSize: '14px', fontWeight: '700', marginBottom: '6px' }}>{item.value}</p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{item.label}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {seccionActiva === 'retos' && (
            <div style={{
              background: 'var(--bg-card)', borderRadius: '18px', padding: '18px',
              border: '1px solid var(--border)', marginBottom: '14px'
            }}>
              <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)' }}>Retos de lectura</p>
              {(resumen.retos || []).length ? (
                resumen.retos.map((reto, index) => (
                  <div key={reto.id || reto.titulo} style={{ marginBottom: index < resumen.retos.length - 1 ? '14px' : '0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <p style={{ fontSize: '13px', fontWeight: '600' }}>{reto.titulo}</p>
                      <p style={{ color: 'var(--accent)', fontSize: '12px', fontWeight: 'bold' }}>{reto.progreso}%</p>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '8px', lineHeight: '1.4' }}>{reto.descripcion}</p>
                    <div style={{ background: 'var(--bg-modal)', borderRadius: '999px', height: '7px', overflow: 'hidden' }}>
                      <div style={{ width: `${reto.progreso}%`, height: '100%', background: 'var(--accent)' }} />
                    </div>
                  </div>
                ))
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Aún no tienes retos registrados.</p>
              )}
            </div>
          )}
          {seccionActiva === 'resenas' && (
            <div style={{
              background: 'var(--bg-card)', borderRadius: '18px', padding: '18px',
              border: '1px solid var(--border)', marginBottom: '14px'
            }}>
              <p style={{ fontWeight: 'bold', marginBottom: '14px', color: 'var(--accent)' }}>Reseñas</p>
              {cargandoResenas ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Cargando reseñas...</p>
              ) : resenas.length ? (
                resenas.map((reseña, index) => (
                  <div key={`${reseña.libro_id}-${index}`} style={{ marginBottom: index < resenas.length - 1 ? '16px' : '0', paddingBottom: '12px', borderBottom: index < resenas.length - 1 ? '1px solid var(--border)' : 'none' }}>
                    <p style={{ fontSize: '14px', fontWeight: '700', marginBottom: '4px' }}>{reseña.titulo}</p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '6px' }}>{reseña.autor}</p>
                    <p style={{ color: 'var(--accent)', fontSize: '12px', marginBottom: '8px' }}>⭐ {reseña.calificacion.toFixed(1)}</p>
                    <p style={{ color: 'var(--text-primary)', fontSize: '13px', lineHeight: '1.6' }}>{reseña.texto}</p>
                  </div>
                ))
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Aún no tienes reseñas publicadas. Escribe tu primera reseña desde tu biblioteca o un libro leído.</p>
              )}
            </div>
          )}
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

const inputStyle = {
  background: 'var(--bg-secondary)', border: '1px solid var(--border)',
  borderRadius: '12px', padding: '12px 14px',
  color: 'var(--text-primary)', fontSize: '14px', outline: 'none', width: '100%'
};

const btnStyle = {
  background: 'var(--accent)', color: 'var(--bg-primary)',
  border: 'none', borderRadius: '14px', padding: '14px',
  fontSize: '15px', fontWeight: 'bold', cursor: 'pointer'
};

const actionButton = {
  background: 'var(--bg-secondary)', color: 'var(--text-primary)',
  border: '1px solid var(--border)', borderRadius: '12px',
  padding: '8px 10px', fontSize: '12px', cursor: 'pointer'
};

const deleteButton = {
  background: 'transparent', color: '#c0635a',
  border: '1px solid #c0635a', borderRadius: '12px',
  padding: '8px 10px', fontSize: '12px', cursor: 'pointer'
};

export default Profile;