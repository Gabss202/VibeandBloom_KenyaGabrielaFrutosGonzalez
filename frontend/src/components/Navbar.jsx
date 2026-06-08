import { Link, useLocation } from 'react-router-dom';
import { HiHome, HiBookOpen, HiSearch, HiUser } from 'react-icons/hi';

const Navbar = () => {
  const location = useLocation();

  const links = [
    { path: '/', icon: <HiHome size={24} />, label: 'Inicio' },
    { path: '/library', icon: <HiBookOpen size={24} />, label: 'Biblioteca' },
    { path: '/search', icon: <HiSearch size={24} />, label: 'Buscar' },
    { path: '/profile', icon: <HiUser size={24} />, label: 'Perfil' },
  ];

  return (
    <nav style={{
      position: 'fixed', bottom: 0, left: 0, right: 0,
      background: 'var(--bg-secondary)',
      borderTop: '1px solid var(--border)',
      display: 'flex', justifyContent: 'space-around',
      padding: '12px 0 20px', zIndex: 100
    }}>
      {links.map(link => (
        <Link key={link.path} to={link.path} style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          gap: '4px', textDecoration: 'none',
          color: location.pathname === link.path ? 'var(--accent)' : 'var(--text-muted)',
          fontSize: '11px'
        }}>
          {link.icon}
          {link.label}
        </Link>
      ))}
    </nav>
  );
};

export default Navbar;