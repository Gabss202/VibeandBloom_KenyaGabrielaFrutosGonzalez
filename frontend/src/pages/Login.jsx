import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const Login = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async () => {
    try {
      const data = new FormData();
      data.append('username', form.username);
      data.append('password', form.password);
      const res = await axios.post('https://fantastic-garbanzo-r47j5ppj6x6xf5w9-8000.app.github.dev/login', data);
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('username', form.username);
      navigate('/');
    } catch {
      setError('Usuario o contraseña incorrectos');
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