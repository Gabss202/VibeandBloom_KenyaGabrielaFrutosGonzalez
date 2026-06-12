import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import API from '../config';

const Login = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [recuperar, setRecuperar] = useState({ identificador: '', nuevaPassword: '' });
  const [modoRecuperacion, setModoRecuperacion] = useState(false);
  const [error, setError] = useState('');
  const [mensajeRecuperacion, setMensajeRecuperacion] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async () => {
    try {
      const body = new URLSearchParams();
      body.append('username', form.username.trim());
      body.append('password', form.password);
      const res = await axios.post(`${API}/login`, body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('username', form.username);
      navigate('/');
    } catch (error) {
      const detalle = error?.response?.data?.detail;
      setError(detalle || 'Usuario o contraseña incorrectos');
    }
  };

  const handleRecuperar = async () => {
    try {
      const res = await axios.post(`${API}/recuperar-password`, {
        identificador: recuperar.identificador.trim(),
        nueva_password: recuperar.nuevaPassword,
      });
      setMensajeRecuperacion(res.data?.mensaje || 'Contraseña actualizada');
      setError('');
    } catch (error) {
      const detalle = error?.response?.data?.detail;
      setError(detalle || 'No se pudo recuperar el acceso');
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', padding: '24px'
    }}>
      <h1 style={{ fontSize: '42px', color: 'var(--accent)', marginBottom: '8px', fontStyle: 'italic' }}>
        Novelia
      </h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '40px' }}>
        Tu app de lectura
      </p>

      <div style={{ width: '100%', maxWidth: '360px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <input
          placeholder="Usuario"
          value={form.username}
          onChange={e => setForm({ ...form, username: e.target.value })}
          style={inputStyle}
        />
        <input
          placeholder="Contraseña"
          type="password"
          value={form.password}
          onChange={e => setForm({ ...form, password: e.target.value })}
          style={inputStyle}
        />

        {error && <p style={{ color: '#e07070', fontSize: '14px', textAlign: 'center' }}>{error}</p>}

        <button
          type="button"
          onClick={() => setModoRecuperacion(prev => !prev)}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            fontSize: '13px',
            cursor: 'pointer',
            textAlign: 'center',
            padding: '0',
          }}
        >
          {modoRecuperacion ? 'Volver al inicio de sesión' : '¿Olvidaste tu contraseña?'}
        </button>

        {modoRecuperacion && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '4px' }}>
            <input
              placeholder="Usuario o email"
              value={recuperar.identificador}
              onChange={e => setRecuperar({ ...recuperar, identificador: e.target.value })}
              style={inputStyle}
            />
            <input
              placeholder="Nueva contraseña"
              type="password"
              value={recuperar.nuevaPassword}
              onChange={e => setRecuperar({ ...recuperar, nuevaPassword: e.target.value })}
              style={inputStyle}
            />
            {mensajeRecuperacion && (
              <p style={{ color: 'var(--accent)', fontSize: '13px', textAlign: 'center' }}>{mensajeRecuperacion}</p>
            )}
            <button onClick={handleRecuperar} style={btnStyle}>
              Restablecer acceso
            </button>
          </div>
        )}

        <button onClick={handleSubmit} style={btnStyle}>
          Iniciar sesión
        </button>

        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '14px' }}>
          ¿No tienes cuenta?{' '}
          <Link to="/register" style={{ color: 'var(--accent)' }}>Regístrate</Link>
        </p>
      </div>
    </div>
  );
};

const inputStyle = {
  background: 'var(--bg-card)',
  border: '1px solid var(--border)',
  borderRadius: '12px',
  padding: '14px 16px',
  color: 'var(--text-primary)',
  fontSize: '15px',
  outline: 'none',
  width: '100%'
};

const btnStyle = {
  background: 'var(--accent)',
  color: 'var(--bg-primary)',
  border: 'none',
  borderRadius: '12px',
  padding: '14px',
  fontSize: '16px',
  fontWeight: 'bold',
  cursor: 'pointer',
  width: '100%'
};

export default Login;