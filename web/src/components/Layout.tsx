/**
 * Main Application Layout
 *
 * Provides sidebar navigation and main content area
 */

import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

export default function Layout() {
  const location = useLocation();
  const { sidebarOpen, toggleSidebar, theme, setTheme } = useAppStore((state) => ({
    sidebarOpen: state.ui.sidebarOpen,
    toggleSidebar: state.toggleSidebar,
    theme: state.ui.theme,
    setTheme: state.setTheme,
  }));

  const isActive = (path: string) => location.pathname === path;

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <div className={`app-layout ${theme}`}>
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>SampleMind AI</h2>
          <button className="sidebar-toggle" onClick={toggleSidebar}>
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <Link
            to="/"
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            <span className="nav-icon">📊</span>
            {sidebarOpen && <span className="nav-text">Dashboard</span>}
          </Link>

          <Link
            to="/analyze"
            className={`nav-link ${isActive('/analyze') ? 'active' : ''}`}
          >
            <span className="nav-icon">🎵</span>
            {sidebarOpen && <span className="nav-text">Analyze</span>}
          </Link>

          <Link
            to="/library"
            className={`nav-link ${isActive('/library') ? 'active' : ''}`}
          >
            <span className="nav-icon">📚</span>
            {sidebarOpen && <span className="nav-text">Library</span>}
          </Link>

          <Link
            to="/generate"
            className={`nav-link ${isActive('/generate') ? 'active' : ''}`}
          >
            <span className="nav-icon">🎨</span>
            {sidebarOpen && <span className="nav-text">Generate</span>}
          </Link>

          <Link
            to="/streaming"
            className={`nav-link ${isActive('/streaming') ? 'active' : ''}`}
          >
            <span className="nav-icon">📡</span>
            {sidebarOpen && <span className="nav-text">Streaming</span>}
          </Link>
        </nav>

        <div className="sidebar-footer">
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
