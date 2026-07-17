import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, BookOpen } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Courses from './pages/Courses';

function Navigation() {
  const location = useLocation();
  
  return (
    <header className="glass-header">
      <div className="flex-center gap-2">
        <div style={{ width: 32, height: 32, borderRadius: 8, background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
          N
        </div>
        <h2 style={{ margin: 0 }} className="text-gradient">نتيجة بلس</h2>
      </div>
      
      <nav className="nav-links">
        <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
          <LayoutDashboard size={20} />
          الرئيسية
        </Link>
        <Link to="/students" className={`nav-link ${location.pathname.startsWith('/students') ? 'active' : ''}`}>
          <Users size={20} />
          الطلاب
        </Link>
        <Link to="/courses" className={`nav-link ${location.pathname.startsWith('/courses') ? 'active' : ''}`}>
          <BookOpen size={20} />
          المقررات
        </Link>
      </nav>
    </header>
  );
}

function App() {
  return (
    <Router>
      <Navigation />
      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/students" element={<Students />} />
          <Route path="/students/:seat" element={<Students />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/courses/:code" element={<Courses />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
