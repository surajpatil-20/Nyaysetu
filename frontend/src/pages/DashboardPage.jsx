import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { casesApi } from '../api/cases';
import { adminApi } from '../api/admin';
import AppLayout from '../components/AppLayout';
import {
  Search,
  Bot,
  Folder,
  Network,
  Scale,
  Building2,
  FileText,
  ArrowRight,
  Sparkles,
  BookOpen,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { Skeleton } from '../components/Skeleton';
import './DashboardPage.css';

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({
    cases: 105,
    courts: 5,
    judges: 78,
    documents: 102,
  });
  const [recentCases, setRecentCases] = useState([]);
  const [loading, setLoading] = useState(true);

  // Time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  useEffect(() => {
    let isMounted = true;

    async function loadDashboardData() {
      setLoading(true);
      try {
        // Query real Supreme Court precedent records for the dashboard
        const promises = [
          casesApi.getCases({ search: 'INSC', limit: 4 }),
        ];

        // RULES 2 & 3: Only request admin statistics if user has the ADMIN role
        const userIsAdmin = isAdmin || user?.role === 'ADMIN';
        if (userIsAdmin) {
          promises.push(adminApi.getStats().catch(() => null));
        }

        const results = await Promise.allSettled(promises);
        if (!isMounted) return;

        const casesResult = results[0];
        if (casesResult.status === 'fulfilled' && casesResult.value) {
          const list = casesResult.value.results || casesResult.value || [];
          setRecentCases(list.slice(0, 4));
        }

        if (userIsAdmin && results[1]) {
          const statsResult = results[1];
          if (statsResult.status === 'fulfilled' && statsResult.value) {
            setStats((prev) => ({
              cases: statsResult.value.cases ?? prev.cases,
              courts: statsResult.value.courts ?? prev.courts,
              judges: statsResult.value.judges ?? prev.judges,
              documents: statsResult.value.documents ?? prev.documents,
            }));
          }
        }
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadDashboardData();

    return () => {
      isMounted = false;
    };
  }, [isAdmin, user?.role]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <AppLayout>
      <div className="dashboard-container">
        {/* Top Header & Greeting */}
        <div className="dashboard-header">
          <p className="dashboard-greeting">
            {getGreeting()}{user?.first_name ? `, ${user.first_name}` : user?.username ? `, ${user.username}` : ''}
          </p>
          <h1 className="dashboard-title">Explore India's Judicial Knowledge</h1>
          <p className="dashboard-subtitle">
            Welcome to your research workspace. Query Supreme Court precedents, inspect case intelligence, and verify grounded evidence.
          </p>
        </div>

        {/* Large Search Bar Card with Quick Actions */}
        <div className="dashboard-search-card">
          <form onSubmit={handleSearchSubmit} className="dashboard-search-form">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search precedents, judgments, legal sections, or citations (e.g. Pradeep v State of Haryana)..."
              className="dashboard-search-input"
            />
            <button
              type="submit"
              className="dashboard-search-submit"
              title="Search Judicial Records"
            >
              <Search className="h-5 w-5" />
            </button>
          </form>

          {/* Quick Actions */}
          <div className="dashboard-quick-actions">
            <span className="text-xs text-slate-500 font-semibold">Quick Actions:</span>
            <Link to="/search" className="dashboard-quick-action-btn">
              <Search className="h-3.5 w-3.5 text-[#FFA425]" />
              <span>Search Cases</span>
            </Link>
            <Link to="/assistant" className="dashboard-quick-action-btn">
              <Bot className="h-3.5 w-3.5 text-[#11486B]" />
              <span>Ask AI Assistant</span>
            </Link>
            <Link to="/documents" className="dashboard-quick-action-btn">
              <Folder className="h-3.5 w-3.5 text-[#11486B]" />
              <span>Upload Document</span>
            </Link>
            <Link to="/graph" className="dashboard-quick-action-btn">
              <Network className="h-3.5 w-3.5 text-[#FFA425]" />
              <span>Explore Knowledge Graph</span>
            </Link>
          </div>
        </div>

        {/* Real Statistics Cards */}
        <div className="dashboard-stats-grid">
          <div className="dashboard-stat-card">
            <div className="dashboard-stat-icon-box">
              <Scale className="h-6 w-6" />
            </div>
            <div className="dashboard-stat-info">
              {loading ? (
                <Skeleton variant="title" width="60px" height="1.75rem" />
              ) : (
                <p className="dashboard-stat-value">{stats.cases}</p>
              )}
              <p className="dashboard-stat-label">Judicial Cases</p>
            </div>
          </div>

          <div className="dashboard-stat-card">
            <div className="dashboard-stat-icon-box">
              <Building2 className="h-6 w-6" />
            </div>
            <div className="dashboard-stat-info">
              {loading ? (
                <Skeleton variant="title" width="40px" height="1.75rem" />
              ) : (
                <p className="dashboard-stat-value">{stats.courts}</p>
              )}
              <p className="dashboard-stat-label">Adjudicating Courts</p>
            </div>
          </div>

          <div className="dashboard-stat-card">
            <div className="dashboard-stat-icon-box">
              <BookOpen className="h-6 w-6" />
            </div>
            <div className="dashboard-stat-info">
              {loading ? (
                <Skeleton variant="title" width="50px" height="1.75rem" />
              ) : (
                <p className="dashboard-stat-value">{stats.judges}</p>
              )}
              <p className="dashboard-stat-label">Coram Judges</p>
            </div>
          </div>

          <div className="dashboard-stat-card">
            <div className="dashboard-stat-icon-box">
              <FileText className="h-6 w-6" />
            </div>
            <div className="dashboard-stat-info">
              {loading ? (
                <Skeleton variant="title" width="55px" height="1.75rem" />
              ) : (
                <p className="dashboard-stat-value">{stats.documents}</p>
              )}
              <p className="dashboard-stat-label">Indexed Documents</p>
            </div>
          </div>
        </div>

        {/* Recent / Important Cases Section */}
        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2 className="dashboard-section-title">Recent & Precedent Cases</h2>
            <Link to="/search" className="dashboard-section-link">
              <span>View All Precedents</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          {loading ? (
            <div className="skeleton-cases-grid" aria-busy="true" aria-live="polite">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="skeleton-case-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem' }}>
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <Skeleton variant="pill" width="90px" height="1.125rem" />
                      <Skeleton variant="title" width="90%" height="1.25rem" />
                    </div>
                    <Skeleton variant="circle" width="1.75rem" height="1.75rem" />
                  </div>
                  <Skeleton variant="text" width="96%" height="0.875rem" />
                  <Skeleton variant="text" width="75%" height="0.875rem" />
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
                    <Skeleton variant="text" width="140px" height="0.75rem" />
                    <Skeleton variant="pill" width="100px" height="1.25rem" />
                  </div>
                </div>
              ))}
            </div>
          ) : recentCases.length > 0 ? (
            <div className="dashboard-cases-grid">
              {recentCases.map((c) => (
                <div key={c.id} className="dashboard-case-card">
                  <div className="dashboard-case-top">
                    <h3 className="dashboard-case-title">
                      <Link to={`/cases/${c.id}`}>
                        {c.case_title || 'Supreme Court Judgment'}
                      </Link>
                    </h3>
                    <div className="dashboard-case-meta">
                      <span className="font-semibold text-slate-700">{c.case_number || 'Docket'}</span>
                      <span>•</span>
                      <span>{c.court_name || 'Supreme Court of India'}</span>
                      {c.decision_date && (
                        <>
                          <span>•</span>
                          <span>{c.decision_date}</span>
                        </>
                      )}
                    </div>

                    {c.description && (
                      <p className="dashboard-case-snippet">
                        {c.description.length > 180 ? `${c.description.slice(0, 177)}...` : c.description}
                      </p>
                    )}
                  </div>

                  <div className="dashboard-case-footer">
                    <span className="dashboard-case-provenance">
                      Verified Supreme Court Record
                    </span>
                    <Link to={`/cases/${c.id}`} className="dashboard-case-btn-view">
                      <span>View Dossier</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 bg-white border border-slate-200 rounded-xl text-center text-xs text-slate-500">
              No recent cases available. Search to explore precedents.
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
