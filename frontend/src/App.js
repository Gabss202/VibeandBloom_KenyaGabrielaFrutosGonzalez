import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Library from './pages/Library';
import Search from './pages/Search';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import Navbar from './components/Navbar';
import './index.css';

function App() {
  const token = localStorage.getItem('token');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={token ? <><Navbar /><Home /></> : <Navigate to="/login" />} />
        <Route path="/library" element={token ? <><Navbar /><Library /></> : <Navigate to="/login" />} />
        <Route path="/search" element={token ? <><Navbar /><Search /></> : <Navigate to="/login" />} />
        <Route path="/profile" element={token ? <><Navbar /><Profile /></> : <Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;