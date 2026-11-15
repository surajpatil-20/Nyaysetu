import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Search,
  Bot,
  Network,
  Folder,
  Building2,
  Info,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import heroImg from '../assets/hero.png';

export default function HomePage() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const quickPills = [
    'child witness testimony',
    'Section 302 IPC circumstantial evidence',
    'anticipatory bail Section 438',
    'speedy trial Article 21',
  ];

  const quickActions = [
    {
      title: 'Search Cases',
      description: 'Precedents, orders & rulings',
      icon: Search,
      link: '/search',
    },
    {
      title: 'Ask Judicial AI',
      description: 'Evidence-grounded answers',
      icon: Bot,
      link: isAuthenticated ? '/assistant' : '/login',
    },
    {
      title: 'Knowledge Graph',
      description: 'Connected cases, judges & acts',
      icon: Network,
      link: '/search',
    },
    {
      title: 'Document Vault',
      description: 'Private OCR & chunk analysis',
      icon: Folder,
      link: '/documents',
    },
    {
      title: 'Official Services',
      description: 'eCourts, NJDG & NALSA portals',
      icon: Building2,
      link: '/services',
    },
  ];

  return (
    <div className="bg-[#F8FAFC] min-h-[calc(100vh-64px)] flex flex-col justify-between">
      {/* Hero Section with Supreme Court Background Image */}
      <section className="relative overflow-hidden bg-gradient-to-b from-[#0A192F] via-[#0E213D] to-[#0A192F] text-white pt-16 pb-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800 flex flex-col items-center justify-center">
        {/* Supreme Court Watermark Background */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden">
          <img
            src={heroImg}
            alt="Supreme Court of India"
            className="w-[440px] sm:w-[560px] md:w-[680px] max-w-none opacity-15 filter drop-shadow-2xl"
          />
          {/* Subtle vignette / gradient overlays */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#0A192F] via-transparent to-[#0A192F]/60" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_30%,_#0A192F_90%)]" />
        </div>

        {/* Hero Foreground Content */}
        <div className="relative z-10 max-w-3xl mx-auto text-center space-y-6">
          {/* Pill Badge */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 bg-blue-500/15 border border-blue-400/30 rounded-full text-blue-300 text-xs font-semibold backdrop-blur-xs">
            <Sparkles className="h-3.5 w-3.5 text-blue-400" />
            <span>AI-Assisted Judicial Information Platform</span>
          </div>

          {/* Heading */}
          <div className="space-y-2">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white drop-shadow-sm">
              NYAYASETU
            </h1>
            <p className="text-sm sm:text-base text-slate-300 max-w-xl mx-auto leading-relaxed">
              Search real Supreme Court precedents, explore case relationships, and ask evidence-grounded legal questions.
            </p>
          </div>

          {/* Centered Large Search Bar */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto mt-4">
            <div className="flex rounded-xl shadow-lg border border-slate-700/80 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 overflow-hidden bg-white">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search cases, judgments, legal concepts..."
                className="flex-1 px-5 py-4 text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
              />
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 flex items-center justify-center transition shadow-xs"
                title="Search Precedents"
              >
                <Search className="h-5 w-5" />
              </button>
            </div>
          </form>

          {/* Quick Search Chips */}
          <div className="pt-1 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-400">
            <span className="text-slate-500 font-medium hidden sm:inline">Try searching:</span>
            {quickPills.map((pill, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => navigate(`/search?q=${encodeURIComponent(pill)}`)}
                className="px-3 py-1 bg-slate-800/80 hover:bg-blue-600 hover:text-white text-slate-300 rounded-lg border border-slate-700/70 transition backdrop-blur-xs text-[11px]"
              >
                {pill}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Main Content: 5 Clean Quick Action Cards */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8">
        {/* Quick Actions Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <Link
                key={idx}
                to={action.link}
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs hover:shadow-md hover:border-blue-400 transition flex flex-col items-center text-center space-y-2 group"
              >
                <div className="p-3 bg-blue-50 text-blue-600 rounded-xl group-hover:bg-blue-600 group-hover:text-white transition shadow-2xs">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm group-hover:text-blue-600 transition">
                    {action.title}
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5 leading-normal">
                    {action.description}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Minimal Informational Note for Logged-Out Users */}
        {!isAuthenticated && (
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs shadow-2xs">
            <div className="flex items-center space-x-3 text-slate-700">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg flex-shrink-0">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <span className="font-bold text-slate-900">Sign in to use the NYAYASETU AI Assistant</span>
                <span className="text-slate-500 hidden sm:inline"> — Evidence-grounded answers with Supreme Court citations require an active account.</span>
              </div>
            </div>
            <Link
              to="/login"
              state={{ from: { pathname: '/assistant' } }}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-xs transition whitespace-nowrap shadow-2xs flex items-center space-x-1"
            >
              <span>Sign In</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        )}

        {/* Civic Disclaimer Alert Banner */}
        <div className="bg-slate-100/80 border border-slate-200 rounded-xl p-3.5 flex items-center space-x-3 text-xs text-slate-600">
          <Info className="h-4 w-4 text-slate-500 flex-shrink-0" />
          <span>
            NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice and does not predict judicial outcomes or make judicial decisions.
          </span>
        </div>
      </section>
    </div>
  );
}
