import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { lawsApi } from '../api/laws';
import AppLayout from '../components/AppLayout';
import {
  BookOpen,
  Search,
  Scale,
  ShoppingBag,
  Car,
  ShieldAlert,
  Home,
  ShieldCheck,
  Briefcase,
  ExternalLink,
  PhoneCall,
  ArrowRight,
  Sparkles,
  HelpCircle,
  X,
  FileText
} from 'lucide-react';
import './KnowYourLawPage.css';

const ICON_MAP = {
  ShoppingBag: ShoppingBag,
  Car: Car,
  ShieldAlert: ShieldAlert,
  Scale: Scale,
  Home: Home,
  ShieldCheck: ShieldCheck,
  Briefcase: Briefcase,
};

export default function KnowYourLawPage() {
  const [categories, setCategories] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategorySlug, setActiveCategorySlug] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [catsRes, scensRes] = await Promise.all([
          lawsApi.getCategories(),
          lawsApi.getScenarios(),
        ]);
        setCategories(Array.isArray(catsRes) ? catsRes : catsRes?.results || []);
        const scList = Array.isArray(scensRes) ? scensRes : scensRes?.results || [];
        setScenarios(scList);
      } catch (err) {
        console.error('Failed to load Know Your Law data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredScenarios = useMemo(() => {
    return scenarios.filter((sc) => {
      // Category filter
      if (activeCategorySlug !== 'ALL' && sc.category_slug !== activeCategorySlug) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const inTitle = sc.title.toLowerCase().includes(q);
        const inSummary = sc.situation_summary.toLowerCase().includes(q);
        const inCat = (sc.category_name || '').toLowerCase().includes(q);
        const inTags = (sc.act_tags || []).some((tag) => tag.toLowerCase().includes(q));
        return inTitle || inSummary || inCat || inTags;
      }
      return true;
    });
  }, [scenarios, activeCategorySlug, searchQuery]);

  return (
    <AppLayout>
      <div className="kyl-page-container">
        {/* Hero Header */}
        <header className="kyl-hero-header">
          <div className="kyl-hero-content">
            <div className="kyl-hero-badge">
              <BookOpen className="h-3.5 w-3.5 text-[#FFA425]" />
              <span>Civic Judicial Awareness &amp; Statutory Guidance</span>
            </div>
            <h1 className="kyl-hero-title">Know Your Law</h1>
            <p className="kyl-hero-desc">
              Understand your legal rights in common real-life Indian situations. Discover relevant statutory Acts, 
              sections, plain-language explanations, and official India Code references without complex legalese.
            </p>
          </div>

          <div className="kyl-hero-stats">
            <div className="kyl-stat-card">
              <span className="kyl-stat-num">{categories.length || '7'}</span>
              <span className="kyl-stat-label">Legal Domains</span>
            </div>
            <div className="kyl-stat-card">
              <span className="kyl-stat-num">{scenarios.length || '7+'}</span>
              <span className="kyl-stat-label">Real Situations</span>
            </div>
            <div className="kyl-stat-card">
              <span className="kyl-stat-num">100%</span>
              <span className="kyl-stat-label">India Code Verified</span>
            </div>
          </div>
        </header>

        {/* Search Toolbar */}
        <div className="kyl-search-bar-box">
          <Search className="h-5 w-5 text-[var(--text-muted)] shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search real-life situations (e.g. refund, hit and run, cyber fraud, police notice, security deposit, domestic abuse, salary)..."
            className="kyl-search-input"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="kyl-clear-btn"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Category Pills Bar */}
        <div className="kyl-category-tabs-container">
          <div className="kyl-category-tabs" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={activeCategorySlug === 'ALL'}
              onClick={() => setActiveCategorySlug('ALL')}
              className={`kyl-cat-pill ${activeCategorySlug === 'ALL' ? 'active' : ''}`}
            >
              <Scale className="h-4 w-4" />
              <span>All Situations</span>
              <span className="kyl-cat-count">{scenarios.length}</span>
            </button>

            {categories.map((cat) => {
              const IconComp = ICON_MAP[cat.icon] || Scale;
              const isActive = activeCategorySlug === cat.slug;

              return (
                <button
                  key={cat.id}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setActiveCategorySlug(cat.slug)}
                  className={`kyl-cat-pill ${isActive ? 'active' : ''}`}
                >
                  <IconComp className="h-4 w-4" />
                  <span>{cat.name}</span>
                  <span className="kyl-cat-count">{cat.scenario_count}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Results Meta */}
        <div className="kyl-results-meta">
          <p className="kyl-results-count">
            Showing <strong>{filteredScenarios.length}</strong> legal {filteredScenarios.length === 1 ? 'scenario' : 'scenarios'}
            {activeCategorySlug !== 'ALL' && ` in ${categories.find(c => c.slug === activeCategorySlug)?.name || ''}`}
            {searchQuery && ` matching "${searchQuery}"`}
          </p>
          {(activeCategorySlug !== 'ALL' || searchQuery) && (
            <button
              type="button"
              onClick={() => {
                setActiveCategorySlug('ALL');
                setSearchQuery('');
              }}
              className="kyl-reset-btn"
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Scenarios Grid */}
        {loading ? (
          <div className="kyl-loading-grid">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="kyl-skeleton-card">
                <div className="kyl-skeleton-line title" />
                <div className="kyl-skeleton-line text" />
                <div className="kyl-skeleton-line text short" />
                <div className="kyl-skeleton-line pill" />
              </div>
            ))}
          </div>
        ) : filteredScenarios.length === 0 ? (
          <div className="kyl-empty-state">
            <HelpCircle className="h-10 w-10 text-[var(--text-light)] mb-2" />
            <h3 className="text-base font-bold text-[var(--text-primary)]">No matching legal situations</h3>
            <p className="text-xs text-[var(--text-muted)] max-w-sm mt-1">
              No scenarios matched your query. Try searching for common terms like &ldquo;refund&rdquo;, &ldquo;police&rdquo;, &ldquo;accident&rdquo;, or &ldquo;salary&rdquo;.
            </p>
            <button
              type="button"
              onClick={() => {
                setActiveCategorySlug('ALL');
                setSearchQuery('');
              }}
              className="mt-3 px-3 py-1.5 text-xs font-semibold bg-[#11486B] text-white rounded-md"
            >
              Browse All Situations
            </button>
          </div>
        ) : (
          <div className="kyl-scenarios-grid">
            {filteredScenarios.map((sc) => (
              <article key={sc.id} className="kyl-scenario-card">
                <div className="kyl-card-header">
                  <span className="kyl-category-badge">
                    {sc.category_name}
                  </span>
                  {sc.helpline_number && (
                    <span className="kyl-helpline-badge">
                      <PhoneCall className="h-3 w-3" />
                      <span>Helpline: {sc.helpline_number}</span>
                    </span>
                  )}
                </div>

                <h3 className="kyl-card-title">
                  <Link to={`/know-your-law/${sc.id}`} className="kyl-title-link">
                    {sc.title}
                  </Link>
                </h3>

                <p className="kyl-card-summary">
                  {sc.situation_summary}
                </p>

                {/* Relevant Statutory Sections */}
                {sc.act_tags && sc.act_tags.length > 0 && (
                  <div className="kyl-act-tags-wrap">
                    <span className="kyl-tags-label">Relevant Law:</span>
                    <div className="kyl-tags-list">
                      {sc.act_tags.map((tag, idx) => (
                        <span key={idx} className="kyl-act-tag">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="kyl-card-footer">
                  <Link to={`/know-your-law/${sc.id}`} className="kyl-view-btn">
                    <span>View Rights &amp; Relevant Law</span>
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}

        {/* Civic Information Disclaimer */}
        <footer className="kyl-disclaimer-box">
          <div className="flex items-start gap-2.5">
            <Scale className="h-4 w-4 text-[#FFA425] shrink-0 mt-0.5" />
            <div className="text-xs text-[var(--text-muted)] leading-relaxed">
              <strong className="text-[var(--text-primary)]">Civic Judicial Awareness Notice: </strong>
              The &ldquo;Know Your Law&rdquo; portal provides informational summaries of statutory rights under enactments of the Parliament of India, 
              sourced from the official India Code repository. It is intended for civic education and legal literacy, not as a substitute for professional legal advice from an enrolled advocate.
            </div>
          </div>
        </footer>
      </div>
    </AppLayout>
  );
}
