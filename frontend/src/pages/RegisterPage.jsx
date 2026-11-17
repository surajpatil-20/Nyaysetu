import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Scale, Lock, User, Mail, AlertCircle, ArrowRight } from 'lucide-react';
import './AuthPages.css';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await register({
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        confirmPassword: formData.confirmPassword,
        role: 'CITIZEN',
      });
      // Navigate to OTP verification page with email state
      navigate('/verify-otp', { state: { email: formData.email.trim().toLowerCase() } });
    } catch (err) {
      setError(err.message || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center px-4 py-12 bg-[#F8FAFC]">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 bg-[#0A192F] rounded-xl text-blue-400 shadow-xs">
            <Scale className="h-7 w-7" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Citizen Registration</h2>
          <p className="text-xs text-slate-500">
            Create your account. A 6-digit verification OTP will be generated.
          </p>
        </div>

        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-3.5 text-rose-800 text-xs flex items-start space-x-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1 text-[11px]">
              Username
            </label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="text"
                required
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="citizen_user"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-lg border border-slate-200 text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1 text-[11px]">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="email"
                required
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="citizen@example.com"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-lg border border-slate-200 text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1 text-[11px]">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="password"
                required
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-lg border border-slate-200 text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 uppercase tracking-wider mb-1 text-[11px]">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="password"
                required
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-lg border border-slate-200 text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-xs transition flex items-center justify-center space-x-1.5 disabled:opacity-50 mt-2"
          >
            <span>{loading ? 'Submitting Registration...' : 'Register'}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="pt-2 text-center text-xs text-slate-500 border-t border-slate-100">
          <span>Already have a citizen account? </span>
          <Link to="/login" className="text-blue-600 font-semibold hover:underline">
            Sign In here
          </Link>
        </div>
      </div>
    </div>
  );
}
