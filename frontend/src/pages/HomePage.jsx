import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Search,
  Bot,
  Network,
  FileText,
  Building2,
  Info,
  Scale,
  ArrowRight
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

  const quickActions = [
    {
      title: 'Search Cases',
      description: 'Find judgments and orders',
      icon: Search,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      link: '/search',
    },
    {
      title: 'Ask Judicial AI',
      description: 'Get evidence-grounded answers',
      icon: Bot,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      link: isAuthenticated ? '/assistant' : '/login',
    },
    {
      title: 'Explore Relationships',
      description: 'See connected cases, judges and laws',
      icon: Network,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      link: '/search',
    },
    {
      title: 'Analyze Documents',
      description: 'Upload and understand your legal documents',
      icon: FileText,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      link: '/documents',
    },
    {
      title: 'Judicial Services',
      description: 'Access official court services',
      icon: Building2,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      link: '/services',
    },
  ];

  return (
    <div className="bg-white min-h-[calc(100vh-64px)] flex flex-col justify-between">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-8 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Left Column: Headlines & Search */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-xs font-semibold">
              <span>AI-Assisted Judicial Information Platform</span>
            </div>

            <div className="space-y-2">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-[#0A192F]">
                NYAYASETU
              </h1>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-800">
                AI-Assisted, Evidence-Oriented Judicial Information Platform
              </h2>
            </div>

            <p className="text-base text-slate-600 leading-relaxed max-w-xl">
              Search judicial cases, explore case relationships, analyze documents, and ask evidence-grounded questions from real Supreme Court judgments.
            </p>

            {/* Main Search Input Form */}
            <form onSubmit={handleSearch} className="max-w-xl mt-4">
              <div className="flex rounded-xl shadow-sm border border-slate-300 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 overflow-hidden bg-white">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search cases, judgments, legal concepts..."
                  className="flex-1 px-4 py-3.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
                />
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-5 flex items-center justify-center transition"
                  title="Search"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </form>
          </div>

          {/* Right Column: Supreme Court Building Graphic */}
          <div className="lg:col-span-5 flex justify-center lg:justify-end">
            <div className="relative max-w-sm sm:max-w-md w-full">
              <img
                src={heroImg}
                alt="Supreme Court of India illustration"
                className="w-full h-auto object-contain opacity-95 drop-shadow-sm"
              />
            </div>
          </div>
        </div>

        {/* Informational Card for Logged-Out Users (Requirement 7) */}
        {!isAuthenticated && (
          <div className="mt-8 bg-blue-50/80 border border-blue-200/80 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs shadow-2xs">
            <div className="flex items-center space-x-3 text-blue-950">
              <div className="p-2.5 bg-blue-600 text-white rounded-lg shadow-2xs">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <p className="font-bold text-slate-900 text-sm">Sign in to use the NYAYASETU AI Assistant.</p>
                <p className="text-slate-600 text-[11px] mt-0.5">
                  Evidence-grounded judicial answers with verified citations require an active citizen account.
                </p>
              </div>
            </div>
            <Link
              to="/login"
              state={{ from: { pathname: '/assistant' } }}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold whitespace-nowrap shadow-xs transition"
            >
              Sign In to Continue
            </Link>
          </div>
        )}

        {/* 5 Quick Action Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mt-8 pt-2">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <Link
                key={idx}
                to={action.link}
                className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-blue-400 transition flex flex-col items-center text-center space-y-2.5 group"
              >
                <div className="p-3 bg-blue-50 text-blue-600 rounded-xl group-hover:bg-blue-600 group-hover:text-white transition">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm group-hover:text-blue-600 transition">
                    {action.title}
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-1 leading-normal">
                    {action.description}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Civic Disclaimer Alert Banner */}
        <div className="mt-8 bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex items-center space-x-3 text-xs text-slate-600">
          <Info className="h-4 w-4 text-slate-500 flex-shrink-0" />
          <span>
            NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice and does not predict judicial outcomes or make judicial decisions.
          </span>
        </div>
      </section>
    </div>
  );
}
