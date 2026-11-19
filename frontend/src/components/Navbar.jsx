import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Scale, Search, Bell, Menu, X, LogOut, Sun, Moon, Settings } from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setUserDropdownOpen(false);
  };

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Search', path: '/search' },
    ...(isAuthenticated ? [{ name: 'Assistant', path: '/assistant' }] : []),
    { name: 'Services', path: '/services' },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header className="navbar-header">
      <div className="navbar-container">
        <div className="navbar-row">
          {/* Logo / Brand */}
          <Link to="/" className="navbar-brand">
            <div className="navbar-brand-icon-box">
              <Scale className="h-5 w-5" />
            </div>
            <span className="navbar-brand-title">NYAYASETU</span>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="navbar-nav">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`navbar-link ${isActive(link.path) ? 'active' : ''}`}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* Right Action Icons & User Auth */}
          <div className="navbar-actions">
            {/* Dark / Light Mode Toggle Button */}
            <button
              type="button"
              onClick={toggleTheme}
              className="navbar-theme-btn"
              title={theme === 'dark' ? 'Switch to Civic Light Mode' : 'Switch to Judicial Dark Mode'}
              aria-label="Toggle Theme Mode"
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="h-3.5 w-3.5 text-[#FFA425]" />
                  <span className="navbar-theme-label">Light</span>
                </>
              ) : (
                <>
                  <Moon className="h-3.5 w-3.5 text-[#38BDF8]" />
                  <span className="navbar-theme-label">Dark</span>
                </>
              )}
            </button>

            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => navigate('/search')}
                  className="navbar-icon-btn"
                  title="Search Cases"
                >
                  <Search className="h-4 w-4" />
                </button>
                <div className="relative">
                  <button
                    type="button"
                    className="navbar-icon-btn relative"
                    title="Notifications"
                  >
                    <Bell className="h-4 w-4" />
                    <span className="navbar-bell-dot"></span>
                  </button>
                </div>

                {/* User Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                    className="navbar-avatar-btn"
                  >
                    <div className="navbar-avatar-circle">
                      {user?.username ? user.username.slice(0, 2).toUpperCase() : 'US'}
                    </div>
                  </button>

                  {userDropdownOpen && (
                    <div className="navbar-dropdown-menu">
                      <div className="navbar-dropdown-header">
                        <p className="navbar-dropdown-name">
                          {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username}
                        </p>
                        <p className="navbar-dropdown-username">@{user?.username}</p>
                        <span className="navbar-dropdown-role">
                          {user?.role || 'Citizen'}
                        </span>
                      </div>

                      <Link
                        to="/dashboard"
                        onClick={() => setUserDropdownOpen(false)}
                        className="navbar-dropdown-link"
                      >
                        Dashboard
                      </Link>
                      <Link
                        to="/documents"
                        onClick={() => setUserDropdownOpen(false)}
                        className="navbar-dropdown-link"
                      >
                        My Documents
                      </Link>
                      <Link
                        to="/profile"
                        onClick={() => setUserDropdownOpen(false)}
                        className="navbar-dropdown-link"
                      >
                        Profile Settings
                      </Link>
                      <Link
                        to="/settings"
                        onClick={() => setUserDropdownOpen(false)}
                        className="navbar-dropdown-link"
                      >
                        Settings &amp; Font Size
                      </Link>
                      {isAdmin && (
                        <Link
                          to="/admin"
                          onClick={() => setUserDropdownOpen(false)}
                          className="navbar-dropdown-link admin-link"
                        >
                          Admin Panel
                        </Link>
                      )}

                      <div className="border-t border-slate-100 my-1"></div>
                      <button
                        onClick={handleLogout}
                        className="navbar-dropdown-logout"
                      >
                        <LogOut className="h-3.5 w-3.5" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="navbar-auth-buttons">
                <Link to="/login" className="navbar-btn-login">
                  Login
                </Link>
                <Link to="/register" className="navbar-btn-register">
                  Register
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="navbar-mobile-toggle">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="navbar-hamburger-btn"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="navbar-mobile-menu">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileMenuOpen(false)}
              className={`navbar-mobile-link ${isActive(link.path) ? 'active' : ''}`}
            >
              {link.name}
            </Link>
          ))}

          {/* Mobile Theme & Settings Row */}
          <div className="navbar-mobile-theme-box">
            <button
              type="button"
              onClick={toggleTheme}
              className="navbar-mobile-theme-btn"
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="h-4 w-4 text-[#FFA425]" />
                  <span>Switch to Light Mode</span>
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4 text-[#38BDF8]" />
                  <span>Switch to Dark Mode</span>
                </>
              )}
            </button>
            <Link
              to="/settings"
              onClick={() => setMobileMenuOpen(false)}
              className="navbar-mobile-settings-btn"
              title="Font & Accessibility Settings"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </Link>
          </div>

          {isAuthenticated ? (
            <div className="border-t border-slate-800 pt-3 space-y-2">
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="navbar-mobile-link"
              >
                Dashboard
              </Link>
              <Link
                to="/documents"
                onClick={() => setMobileMenuOpen(false)}
                className="navbar-mobile-link"
              >
                My Documents
              </Link>
              {isAdmin && (
                <Link
                  to="/admin"
                  onClick={() => setMobileMenuOpen(false)}
                  className="navbar-mobile-link text-blue-400"
                >
                  Admin Panel
                </Link>
              )}
              <Link
                to="/profile"
                onClick={() => setMobileMenuOpen(false)}
                className="navbar-mobile-link"
              >
                Profile Settings
              </Link>
              <Link
                to="/settings"
                onClick={() => setMobileMenuOpen(false)}
                className="navbar-mobile-link"
              >
                Settings &amp; Font Size
              </Link>
              <button
                onClick={handleLogout}
                className="w-full text-left px-3 py-2 text-sm text-rose-400 hover:bg-slate-800 rounded-lg flex items-center space-x-2"
              >
                <LogOut className="h-4 w-4" />
                <span>Sign Out</span>
              </button>
            </div>
          ) : (
            <div className="border-t border-slate-800 pt-3 flex space-x-3">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="flex-1 text-center py-2 bg-white text-[#0A192F] font-semibold text-xs rounded-lg"
              >
                Login
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="flex-1 text-center py-2 bg-blue-600 text-white font-semibold text-xs rounded-lg"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
