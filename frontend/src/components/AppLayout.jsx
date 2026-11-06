import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Search,
  Bot,
  Folder,
  Building2,
  Shield,
  User,
  Scale
} from 'lucide-react';

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
    <div className="flex min-h-[calc(100vh-64px)] bg-[#F8FAFC]">
      {/* Dark Sidebar */}
      <aside className="w-56 bg-[#0A192F] text-slate-300 flex-shrink-0 hidden md:flex flex-col border-r border-[#1E293B] shadow-sm">
        {/* Sidebar Navigation */}
        <div className="p-4 space-y-1 flex-1">
          {sidebarLinks.map((item) => {
            const Icon = item.icon;
            const active = isLinkActive(item);

            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? 'bg-blue-600 text-white shadow-sm font-semibold'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/70'
                }`}
              >
                <Icon className={`h-4 w-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </div>

        {/* Sidebar Footer */}
        {user && (
          <div className="p-4 border-t border-slate-800/80">
            <Link
              to="/profile"
              className="flex items-center space-x-2.5 px-2 py-1.5 rounded-lg hover:bg-slate-800/60 text-xs text-slate-400 hover:text-slate-200 transition"
            >
              <div className="h-7 w-7 rounded-full bg-blue-600 text-white font-bold text-[11px] flex items-center justify-center">
                {user.username ? user.username.slice(0, 2).toUpperCase() : 'U'}
              </div>
              <div className="truncate">
                <p className="font-semibold text-slate-200 text-xs truncate">
                  {user.first_name ? `${user.first_name}` : user.username}
                </p>
                <p className="text-[10px] text-slate-500 capitalize">{user.role || 'Citizen'}</p>
              </div>
            </Link>
          </div>
        )}
      </aside>

      {/* Main Content Pane */}
      <main className="flex-1 overflow-x-hidden min-w-0">
        {children}
      </main>
    </div>
  );
}

