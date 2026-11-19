import { useState, useEffect } from 'react';
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
  Briefcase,
  Menu,
  X
} from 'lucide-react';
import './AppLayout.css';

export default function AppLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  // Automatically close mobile drawer when route changes
  useEffect(() => {
    setMobileDrawerOpen(false);
  }, [location.pathname]);

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

  const getActivePageTitle = () => {
    if (location.pathname === '/dashboard') return 'Dashboard';
    if (location.pathname === '/search') return 'Search Cases';
    if (location.pathname === '/assistant') return 'AI Assistant';
    if (location.pathname.includes('/graph')) return 'Knowledge Graph';
    if (location.pathname.startsWith('/cases')) return 'Case Dossier';
    if (location.pathname.startsWith('/documents')) return 'Document Vault';
    if (location.pathname === '/services') return 'Judicial Services';
    if (location.pathname === '/settings') return 'Settings';
    if (location.pathname === '/profile') return 'Profile';
    if (location.pathname === '/admin') return 'Admin Panel';
    return 'Legal Workspace';
  };

  return (
    <div className="app-layout-root">
      {/* Mobile Workspace Top Navigation Bar (Visible only on screens < 768px) */}
      <div className="app-mobile-workspace-bar">
        <button
          type="button"
          onClick={() => setMobileDrawerOpen(true)}
          className="app-mobile-drawer-btn"
          aria-label="Open Workspace Navigation Drawer"
        >
          <Menu className="h-5 w-5 text-[#FFA425]" />
          <span className="app-mobile-workspace-title">{getActivePageTitle()}</span>
        </button>

        <div className="app-mobile-workspace-actions">
          <Link to="/search" className="app-mobile-quick-btn" title="Search Precedents">
            <Search className="h-4 w-4" />
          </Link>
          <Link to="/settings" className="app-mobile-quick-btn" title="Settings &amp; Theme">
            <Settings className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {/* Mobile Drawer Backdrop Overlay */}
      {mobileDrawerOpen && (
        <div
          className="app-drawer-backdrop"
          onClick={() => setMobileDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Modern Left Sidebar (Desktop + Mobile Slide-out Drawer) */}
      <aside className={`app-sidebar ${mobileDrawerOpen ? 'mobile-open' : ''}`}>
        {/* Sidebar Brand Header */}
        <div className="app-sidebar-brand">
          <div className="flex items-center justify-between w-full">
            <Link to="/" className="app-sidebar-brand-title">
              <Scale className="app-sidebar-brand-icon" />
              <span>NYAYASETU</span>
            </Link>
            {/* Close Button on Mobile Drawer */}
            <button
              type="button"
              onClick={() => setMobileDrawerOpen(false)}
              className="app-sidebar-close-btn md:hidden"
              aria-label="Close sidebar drawer"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
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
                onClick={() => setMobileDrawerOpen(false)}
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
                onClick={() => setMobileDrawerOpen(false)}
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
              <Link
                to="/profile"
                className="app-sidebar-user-card"
                onClick={() => setMobileDrawerOpen(false)}
              >
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
                className={`app-sidebar-action-btn ${location.pathname === '/profile' ? 'active-action text-white' : ''}`}
                onClick={() => setMobileDrawerOpen(false)}
              >
                <User className="h-4 w-4" />
                <span>Profile</span>
              </Link>

              <Link
                to="/settings"
                className={`app-sidebar-action-btn ${location.pathname === '/settings' ? 'active-action text-white' : ''}`}
                onClick={() => setMobileDrawerOpen(false)}
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
                onClick={() => setMobileDrawerOpen(false)}
              >
                Citizen Login
              </Link>
              <Link
                to="/register"
                className="block text-center py-2 px-3 bg-[#11486B] text-white font-semibold text-xs rounded-md border border-[#FFA425]/40 hover:bg-[#0E3550] transition"
                onClick={() => setMobileDrawerOpen(false)}
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

      {/* Mobile Bottom Navigation Bar (Ultra-responsive one-thumb workspace bar on < 768px) */}
      <nav className="app-mobile-bottom-bar" aria-label="Mobile Navigation">
        <Link
          to="/dashboard"
          className={`app-mobile-bottom-item ${location.pathname === '/dashboard' ? 'active' : ''}`}
        >
          <LayoutDashboard className="h-4 w-4" />
          <span>Home</span>
        </Link>
        <Link
          to="/search"
          className={`app-mobile-bottom-item ${location.pathname.startsWith('/search') || location.pathname.startsWith('/cases') ? 'active' : ''}`}
        >
          <Search className="h-4 w-4" />
          <span>Search</span>
        </Link>
        {isAuthenticated && (
          <Link
            to="/assistant"
            className={`app-mobile-bottom-item ${location.pathname === '/assistant' ? 'active' : ''}`}
          >
            <Bot className="h-4 w-4" />
            <span>AI Chat</span>
          </Link>
        )}
        <Link
          to="/graph"
          className={`app-mobile-bottom-item ${location.pathname.includes('/graph') ? 'active' : ''}`}
        >
          <Network className="h-4 w-4" />
          <span>Graph</span>
        </Link>
        <button
          type="button"
          onClick={() => setMobileDrawerOpen(true)}
          className="app-mobile-bottom-item"
        >
          <Menu className="h-4 w-4" />
          <span>Menu</span>
        </button>
      </nav>
    </div>
  );
}
