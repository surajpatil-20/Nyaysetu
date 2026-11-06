import { useAuth } from '../context/AuthContext';
import { User, Mail, Shield, LogOut, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../components/AppLayout';

export default function ProfilePage() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <AppLayout>
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Citizen Profile & Account</h1>
          <p className="text-xs text-slate-500 mt-0.5">Manage your credentials and access permissions.</p>
        </div>

        {/* Profile Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-5">
            <div className="flex items-center space-x-3.5">
              <div className="h-12 w-12 rounded-full bg-[#0A192F] text-blue-400 font-bold text-base flex items-center justify-center shadow-xs">
                {user?.username ? user.username.slice(0, 2).toUpperCase() : 'US'}
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">
                  {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username}
                </h2>
                <span className="text-xs text-slate-500 font-mono">@{user?.username}</span>
              </div>
            </div>

            <span className="text-xs font-semibold px-3 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-full uppercase tracking-wider">
              {user?.role || 'Citizen'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-slate-50 border border-slate-200/60 rounded-xl space-y-1">
              <span className="text-slate-400 font-semibold uppercase flex items-center space-x-1.5">
                <Mail className="h-3.5 w-3.5" />
                <span>Email Address</span>
              </span>
              <span className="font-medium text-slate-800 text-sm block">{user?.email || 'citizen@nyaysetu.gov.in'}</span>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200/60 rounded-xl space-y-1">
              <span className="text-slate-400 font-semibold uppercase flex items-center space-x-1.5">
                <Shield className="h-3.5 w-3.5" />
                <span>Security Clearance</span>
              </span>
              <span className="font-medium text-slate-800 text-sm block">
                {isAdmin ? 'System Administrator' : 'Standard Citizen Access'}
              </span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 flex justify-between items-center">
            <div className="flex items-center space-x-1.5 text-xs text-emerald-700 font-medium">
              <CheckCircle2 className="h-4 w-4" />
              <span>Multi-tenant isolation active</span>
            </div>

            <button
              type="button"
              onClick={handleLogout}
              className="px-4 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition"
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
