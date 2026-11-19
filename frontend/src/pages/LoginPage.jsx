import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Scale, Lock, User, AlertCircle, CheckCircle2 } from 'lucide-react';
import './AuthPages.css';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';
  const successBanner = location.state?.message || '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Invalid username or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const isUnverifiedAccount = error.toLowerCase().includes('not verified');

  return (
    <div className="auth-page-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-brand-icon-box">
            <Scale className="h-7 w-7" />
          </div>
          <h2 className="auth-title">Citizen Sign In</h2>
          <p className="auth-subtitle">
            Access your secure document vault and evidence-grounded AI Assistant.
          </p>
        </div>

        {/* Success Banner from OTP Verification */}
        {successBanner && (
          <div className="auth-banner-success">
            <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5 text-emerald-600" />
            <span style={{ fontWeight: 600 }}>{successBanner}</span>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="auth-banner-error">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
            <div>
              <span>{error}</span>
              {isUnverifiedAccount && (
                <div>
                  <Link
                    to="/verify-otp"
                    style={{ color: 'var(--primary-navy)', fontWeight: 700, textDecoration: 'underline', marginTop: '0.25rem', display: 'inline-block' }}
                  >
                    Enter your OTP code now &rarr;
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label className="auth-label">Username</label>
            <div className="auth-input-wrapper">
              <User className="auth-input-icon" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="citizen_user"
                className="auth-input"
              />
            </div>
          </div>

          <div className="auth-field">
            <label className="auth-label">Password</label>
            <div className="auth-input-wrapper">
              <Lock className="auth-input-icon" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="auth-input"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="auth-submit-btn"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="auth-footer-text">
          New citizen researcher?{' '}
          <Link to="/register" className="auth-footer-link">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
