import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AppLayout from '../components/AppLayout';
import {
  Search,
  Bot,
  Folder,
  Building2,
  Shield,
  Upload,
  FileText,
  ArrowRight,
  Scale,
  Sparkles,
  Network
} from 'lucide-react';

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();

  const actions = [
    {
      title: 'Hybrid Case Search',
      description: 'Search 100+ Supreme Court judgments using keyword and pgvector semantic retrieval.',
      icon: Search,
      link: '/search',
      cta: 'Explore Precedents',
    },
    {
      title: 'Judicial AI Assistant',
      description: 'Ask evidence-grounded questions with verifiable citations and document page numbers.',
      icon: Bot,
      link: '/assistant',
      cta: 'Start Legal Query',
    },
    {
      title: 'Private Document Vault',
      description: 'Upload legal briefs and documents for isolated OCR extraction and paragraph chunking.',
      icon: Folder,
      link: '/documents',
      cta: 'View My Vault',
    },
    {
      title: 'Official Judicial Services',
      description: 'Direct access to official eCourts, Supreme Court cause lists, and NALSA legal aid.',
      icon: Building2,
      link: '/services',
      cta: 'Browse Portals',
    },
  ];

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Welcome Banner */}
        <div className="bg-[#0A192F] border border-slate-800 rounded-xl p-6 text-white shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <span className="text-[11px] font-semibold px-2.5 py-0.5 bg-blue-500/20 text-blue-300 rounded border border-blue-500/30 uppercase tracking-wider">
              {user?.role || 'Citizen'} Workspace
            </span>
            <h1 className="text-xl sm:text-2xl font-bold mt-2 tracking-tight">
              Welcome back, {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username}!
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Access verified Supreme Court precedents, pgvector semantic search, and analyze private legal documents.
            </p>
          </div>

          <div className="flex space-x-2.5 flex-shrink-0">
            <Link
              to="/documents"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition"
            >
              <Upload className="h-3.5 w-3.5" />
              <span>Upload PDF</span>
            </Link>
            {isAdmin && (
              <Link
                to="/admin"
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition"
              >
                <Shield className="h-3.5 w-3.5 text-blue-400" />
                <span>Admin Panel</span>
              </Link>
            )}
          </div>
        </div>

        {/* 4 Feature Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {actions.map((act, i) => {
            const Icon = act.icon;
            return (
              <Link
                key={i}
                to={act.link}
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs hover:shadow-md hover:border-blue-400 transition group flex flex-col justify-between space-y-3"
              >
                <div className="space-y-2.5">
                  <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl w-fit group-hover:bg-blue-600 group-hover:text-white transition">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-slate-900 text-sm group-hover:text-blue-600 transition">
                    {act.title}
                  </h3>
                  <p className="text-xs text-slate-500 leading-normal">
                    {act.description}
                  </p>
                </div>

                <div className="text-xs text-blue-600 font-semibold flex items-center pt-2">
                  <span>{act.cta}</span>
                  <ArrowRight className="h-3.5 w-3.5 ml-1" />
                </div>
              </Link>
            );
          })}
        </div>

        {/* Quick Search Suggestions */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3">
          <h3 className="font-bold text-slate-900 text-sm">Suggested Research Queries</h3>
          <div className="flex flex-wrap gap-2 text-xs">
            {[
              "child witness testimony in Pradeep v State of Haryana",
              "Section 302 IPC circumstantial evidence",
              "anticipatory bail parameters under Section 438 CrPC",
              "right to speedy trial under Article 21",
            ].map((q, idx) => (
              <Link
                key={idx}
                to={`/search?q=${encodeURIComponent(q)}`}
                className="px-3 py-1.5 bg-slate-50 hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 rounded-lg transition"
              >
                {q}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
