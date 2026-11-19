import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Search,
  Bot,
  Folder,
  Building2,
  Shield,
  Network,
  Scale,
  User,
  Settings,
  LogOut,
  Briefcase
} from 'lucide-react';
import './AppLayout.css';

export default function AppLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const primaryLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Search Cases', path: '/search', icon: Search },
    ...(isAuthenticated ? [{ name: 'AI Assistant', path: '/assistant', icon: Bot }] : []),
    { name: 'Cases', path: '/cases', icon: Briefcase, matchExact: false },
    { name: 'Knowledge Graph', path: '/graph', icon: Network, matchSubpaths: ['/graph', '/cases/'] },
    { name: 'Documents', path: '/documents', icon: Folder },
    { name: 'Judicial Services', path: '/services', icon: Building2 },
  ];

  const isLinkActive = (item) => {
    if (location.pathname === item.path) return true;
    if (item.name === 'Knowledge Graph' && location.pathname.includes('/graph')) return true;
    if (item.name === 'Cases' && location.pathname.startsWith('/cases') && !location.pathname.includes('/graph')) return true;
    if (item.matchSubpaths) {
      return item.matchSubpaths.some((sub) => location.pathname.startsWith(sub));
    }
    return false;
  };

  return (
    <div className="app-layout-root">
      {/* Modern Desktop Left Sidebar */}
      <aside className="app-sidebar">
        {/* Sidebar Brand Header */}
        <div className="app-sidebar-brand">
          <Link to="/" className="app-sidebar-brand-title">
            <Scale className="app-sidebar-brand-icon" />
            <span>NYAYASETU</span>
          </Link>
          <p className="app-sidebar-brand-tagline">Judicial Intelligence</p>
        </div>

        {/* Sidebar Navigation */}
        <div className="app-sidebar-nav">
          <div className="app-sidebar-nav-section-title">Legal Workspace</div>
          {primaryLinks.map((item) => {
            const Icon = item.icon;
            const active = isLinkActive(item);

            return (
              <Link
                key={item.name}
                to={item.path}
                className={`app-sidebar-link ${active ? 'active' : ''}`}
              >
                <Icon className="app-sidebar-link-icon" />
                <span>{item.name}</span>
              </Link>
            );
          })}

          {isAdmin && (
            <>
              <div className="app-sidebar-nav-section-title">Administration</div>
              <Link
                to="/admin"
                className={`app-sidebar-link admin-link ${location.pathname === '/admin' ? 'active' : ''}`}
              >
                <Shield className="app-sidebar-link-icon" />
                <span>Admin Dashboard</span>
              </Link>
            </>
          )}
        </div>

        {/* Sidebar Lower Section: Profile & Actions */}
        <div className="app-sidebar-footer">
          {isAuthenticated && user ? (
            <>
              <Link to="/profile" className="app-sidebar-user-card">
                <div className="app-sidebar-avatar">
                  {user.username ? user.username.slice(0, 2).toUpperCase() : 'U'}
                </div>
                <div className="app-sidebar-user-info">
                  <p className="app-sidebar-username">
                    {user.first_name ? `${user.first_name} ${user.last_name || ''}` : user.username}
                  </p>
                  <p className="app-sidebar-user-role">{user.role || 'Citizen'}</p>
                </div>
              </Link>

              <Link
                to="/profile"
                className={`app-sidebar-action-btn ${location.pathname === '/profile' ? 'text-white' : ''}`}
              >
                <User className="h-4 w-4" />
                <span>Profile</span>
              </Link>

              <Link
                to="/settings"
                className={`app-sidebar-action-btn ${location.pathname === '/settings' ? 'active-action text-white' : ''}`}
              >
                <Settings className="h-4 w-4" />
                <span>Settings</span>
              </Link>

              <button
                type="button"
                onClick={handleLogout}
                className="app-sidebar-action-btn logout-btn"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <div className="p-2 space-y-2">
              <Link
                to="/login"
                className="block text-center py-2 px-3 bg-white text-[#0A2540] font-semibold text-xs rounded-md shadow-xs hover:bg-slate-100 transition"
              >
                Citizen Login
              </Link>
              <Link
                to="/register"
                className="block text-center py-2 px-3 bg-[#11486B] text-white font-semibold text-xs rounded-md border border-[#FFA425]/40 hover:bg-[#0E3550] transition"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Pane */}
      <main className="app-main-pane">
        {children}
      </main>
    </div>
  );
}
