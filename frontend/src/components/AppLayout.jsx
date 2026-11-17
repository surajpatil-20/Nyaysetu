import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Search,
  Bot,
  Folder,
  Building2,
  Shield
} from 'lucide-react';
import './AppLayout.css';

export default function AppLayout({ children }) {
  const location = useLocation();
  const { user, isAuthenticated, isAdmin } = useAuth();

  const sidebarLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Search', path: '/search', icon: Search, matchSubpaths: ['/cases'] },
    ...(isAuthenticated ? [{ name: 'Assistant', path: '/assistant', icon: Bot }] : []),
    { name: 'Documents', path: '/documents', icon: Folder },
    { name: 'Services', path: '/services', icon: Building2 },
  ];

  if (isAdmin) {
    sidebarLinks.push({ name: 'Admin', path: '/admin', icon: Shield });
  }

  const isLinkActive = (item) => {
    if (location.pathname === item.path) return true;
    if (item.matchSubpaths) {
      return item.matchSubpaths.some((sub) => location.pathname.startsWith(sub));
    }
    return false;
  };

  return (
    <div className="app-layout-root">
      {/* Dark Sidebar */}
      <aside className="app-sidebar">
        {/* Sidebar Navigation */}
        <div className="app-sidebar-nav">
          {sidebarLinks.map((item) => {
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
        </div>

        {/* Sidebar Footer */}
        {user && (
          <div className="app-sidebar-footer">
            <Link
              to="/profile"
              className="app-sidebar-user-card"
            >
              <div className="app-sidebar-avatar">
                {user.username ? user.username.slice(0, 2).toUpperCase() : 'U'}
              </div>
              <div className="app-sidebar-user-info">
                <p className="app-sidebar-username">
                  {user.first_name ? `${user.first_name}` : user.username}
                </p>
                <p className="app-sidebar-user-role">{user.role || 'Citizen'}</p>
              </div>
            </Link>
          </div>
        )}
      </aside>

      {/* Main Content Pane */}
      <main className="app-main-pane">
        {children}
      </main>
    </div>
  );
}
