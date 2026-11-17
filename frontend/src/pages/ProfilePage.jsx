import { useAuth } from '../context/AuthContext';
import { Mail, Shield, LogOut, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import './ProfilePage.css';

export default function ProfilePage() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <AppLayout>
      <div className="profile-container">
        {/* Header */}
        <div>
          <h1 className="profile-page-title">Citizen Profile &amp; Account</h1>
          <p className="profile-page-subtitle">Manage your credentials and access permissions.</p>
        </div>

        {/* Profile Card */}
        <div className="profile-card">
          <div className="profile-header-row">
            <div className="profile-user-left">
              <div className="profile-large-avatar">
                {user?.username ? user.username.slice(0, 2).toUpperCase() : 'NS'}
              </div>
              <div className="profile-user-names">
                <h2 className="profile-fullname">
                  {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username || 'Verified Legal Researcher'}
                </h2>
                <span className="profile-username">@{user?.username || 'citizen'}</span>
              </div>
            </div>

            <span className="profile-role-badge">
              {user?.role || 'Citizen'}
            </span>
          </div>

          <div className="profile-info-grid">
            <div className="profile-info-box">
              <span className="profile-info-label">
                <Mail className="h-3.5 w-3.5 text-slate-400" />
                <span>Email Address</span>
              </span>
              <span className="profile-info-val">{user?.email || 'citizen@nyaysetu.gov.in'}</span>
            </div>

            <div className="profile-info-box">
              <span className="profile-info-label">
                <Shield className="h-3.5 w-3.5 text-slate-400" />
                <span>Security Clearance</span>
              </span>
              <span className="profile-info-val">
                {isAdmin ? 'System Administrator' : 'Standard Judicial Access'}
              </span>
            </div>
          </div>

          <div className="profile-footer-row">
            <div className="profile-security-status">
              <CheckCircle2 className="h-4 w-4" />
              <span>Multi-tenant session isolation active</span>
            </div>

            <button
              type="button"
              onClick={handleLogout}
              className="profile-btn-logout"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
