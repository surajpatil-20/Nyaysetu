import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchApi } from '../api/search';
import { casesApi } from '../api/cases';
import EvidenceCard from '../components/EvidenceCard';
import AppLayout from '../components/AppLayout';
import {
  Search,
  RotateCcw,
  SlidersHorizontal,
  AlertCircle,
  FileSearch,
  BookOpen,
  Scale
} from 'lucide-react';
import './SearchPage.css';

const QUICK_TOPICS = [
  { label: 'All Cases', query: '' },
  { label: 'Natural Justice', query: 'natural justice' },
  { label: 'Motor Accident', query: 'accident' },
  { label: 'Income Tax', query: 'income tax' },
  { label: 'Criminal Appeals', query: 'appeal' },
  { label: 'Child Witness', query: 'child witness testimony' },
];

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';

  const [query, setQuery] = useState(queryParam);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isBrowseMode, setIsBrowseMode] = useState(!queryParam);

  // Filters matching Screen 2
  const [court, setCourt] = useState('Supreme Court of India');
  const [startYear, setStartYear] = useState('1950');
  const [endYear, setEndYear] = useState('2024');
  const [judge, setJudge] = useState('');
  const [act, setAct] = useState('');
  const [section, setSection] = useState('');
  const [sortBy, setSortBy] = useState('relevance');

  // Load all cases when no search query is specified
  const loadAllCases = async () => {
    setLoading(true);
    setError(null);
    setIsBrowseMode(true);
    try {
      const data = await casesApi.getCases({ limit: 30 });
      const rawCases = data.results || data || [];
      const mapped = rawCases.map((c) => ({
        case_id: c.id,
        case_number: c.case_number,
        case_title: c.case_title,
        document_title: c.court_name || 'Supreme Court Judgment',
        page_number: 1,
        snippet: c.description || `Supreme Court decision in ${c.case_title}. Presiding forum: ${c.court_name || 'Supreme Court of India'}. Status: ${c.status || 'Disposed'}.`,
        hybrid_score: 1.0,
        source_url: c.source_url,
      }));
      setResults(mapped);
    } catch (err) {
      setError(err.message || 'Failed to load case precedents.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      loadAllCases();
      return;
    }

    setLoading(true);
    setError(null);
    setIsBrowseMode(false);

    try {
      const data = await searchApi.hybridSearch({
        q: searchQuery,
        year: endYear !== '2024' || startYear !== '1950' ? endYear : undefined,
        alpha: 0.5,
        top_k: 25,
      });
      setResults(data.results || []);
    } catch (err) {
      setError(err.message || 'An error occurred while executing search.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (queryParam) {
      setQuery(queryParam);
      performSearch(queryParam);
    } else {
      loadAllCases();
    }
  }, [queryParam]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query.trim() });
      performSearch(query.trim());
    } else {
      setSearchParams({});
      loadAllCases();
    }
  };

  const handleQuickTopic = (topicQuery) => {
    setQuery(topicQuery);
    if (topicQuery) {
      setSearchParams({ q: topicQuery });
      performSearch(topicQuery);
    } else {
      setSearchParams({});
      loadAllCases();
    }
  };

  const handleResetFilters = () => {
    setCourt('Supreme Court of India');
    setStartYear('1950');
    setEndYear('2024');
    setJudge('');
    setAct('');
    setSection('');
    if (query.trim()) {
      performSearch(query.trim());
    } else {
      loadAllCases();
    }
  };

  return (
    <AppLayout>
      <div className="search-page-container">
        <div className="search-layout-grid">
          {/* Left Column: Filters Card (Screen 2) */}
          <div className="search-filters-card">
            <div className="search-filters-header">
              <h3 className="search-filters-title">
                <SlidersHorizontal className="h-4 w-4 text-blue-600" />
                <span>Filters</span>
              </h3>
              <button
                type="button"
                onClick={handleResetFilters}
                className="search-filters-reset-btn"
              >
                <RotateCcw className="h-3 w-3" />
                <span>Reset</span>
              </button>
            </div>

            {/* Filter Form */}
            <div className="flex flex-col gap-4 text-xs">
              {/* Court */}
              <div className="search-filter-group">
                <label className="search-filter-label">Court</label>
                <select
                  value={court}
                  onChange={(e) => setCourt(e.target.value)}
                  className="search-filter-select"
                >
                  <option value="Supreme Court of India">Supreme Court of India</option>
                  <option value="High Court of Delhi">High Court of Delhi</option>
                  <option value="High Court of Bombay">High Court of Bombay</option>
                  <option value="High Court of Rajasthan">High Court of Rajasthan</option>
                </select>
              </div>

              {/* Year Range */}
              <div className="search-filter-group">
                <label className="search-filter-label">Year Range</label>
                <div className="search-filter-year-grid">
                  <input
                    type="number"
                    value={startYear}
                    onChange={(e) => setStartYear(e.target.value)}
                    placeholder="1950"
                    min="1950"
                    max="2026"
                    className="search-filter-input"
                  />
                  <input
                    type="number"
                    value={endYear}
                    onChange={(e) => setEndYear(e.target.value)}
                    placeholder="2024"
                    min="1950"
                    max="2026"
                    className="search-filter-input"
                  />
                </div>
              </div>

              {/* Judge */}
              <div className="search-filter-group">
                <label className="search-filter-label">Presiding Judge</label>
                <select
                  value={judge}
                  onChange={(e) => setJudge(e.target.value)}
                  className="search-filter-select"
                >
                  <option value="">All Judges (78 Coram)</option>
                  <option value="A.S. Bopanna">Justice A.S. Bopanna</option>
                  <option value="Abhay S. Oka">Justice Abhay S. Oka</option>
                  <option value="Prashant Kumar Mishra">Justice Prashant Kumar Mishra</option>
                  <option value="D.Y. Chandrachud">Chief Justice D.Y. Chandrachud</option>
                  <option value="Priya Sharma">Justice Priya Sharma</option>
                  <option value="Arun Kumar">Justice Arun Kumar</option>
                </select>
              </div>

              {/* Act */}
              <div className="search-filter-group">
                <label className="search-filter-label">Enactment / Act</label>
                <select
                  value={act}
                  onChange={(e) => setAct(e.target.value)}
                  className="search-filter-select"
                >
                  <option value="">All Statutes</option>
                  <option value="Indian Penal Code, 1860">Indian Penal Code, 1860</option>
                  <option value="Code of Criminal Procedure, 1973">Code of Criminal Procedure, 1973</option>
                  <option value="Constitution of India">Constitution of India</option>
                  <option value="Indian Evidence Act, 1872">Indian Evidence Act, 1872</option>
                  <option value="Income Tax Act, 1961">Income Tax Act, 1961</option>
                  <option value="Motor Vehicles Act, 1988">Motor Vehicles Act, 1988</option>
                </select>
              </div>

              {/* Section */}
              <div className="search-filter-group">
                <label className="search-filter-label">Section / Article</label>
                <select
                  value={section}
                  onChange={(e) => setSection(e.target.value)}
                  className="search-filter-select"
                >
                  <option value="">All Sections</option>
                  <option value="Section 302">Section 302 IPC (Murder)</option>
                  <option value="Section 34">Section 34 IPC (Common Intention)</option>
                  <option value="Section 438">Section 438 CrPC (Anticipatory Bail)</option>
                  <option value="Article 21">Article 21 (Life & Liberty)</option>
                  <option value="Section 118">Section 118 Evidence Act</option>
                  <option value="Section 166">Section 166 Motor Vehicles Act</option>
                </select>
              </div>

              {/* Apply Filters Button */}
              <button
                type="button"
                onClick={() => performSearch(query)}
                className="search-filters-apply-btn"
              >
                Apply Filters
              </button>
            </div>
          </div>

          {/* Right Column: Search Input & Results (Screen 2) */}
          <div className="search-main-column">
            {/* Search Input Bar */}
            <form onSubmit={handleSubmit} className="w-full">
              <div className="search-bar-box">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search across 105 precedents (e.g. tax, accident, appeal, natural justice, bail)..."
                  className="search-bar-input"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="search-bar-submit"
                  title="Execute Hybrid Search"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </form>

            {/* Quick Topic Buttons */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Explore Topics:</span>
              {QUICK_TOPICS.map((topic, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleQuickTopic(topic.query)}
                  style={{
                    padding: '0.25rem 0.625rem',
                    borderRadius: 'var(--radius-full)',
                    border: '1px solid var(--border-subtle)',
                    backgroundColor: query === topic.query ? 'var(--primary-navy)' : '#ffffff',
                    color: query === topic.query ? '#ffffff' : 'var(--text-secondary)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    fontSize: '0.6875rem',
                    transition: 'all var(--transition-fast)'
                  }}
                >
                  {topic.label}
                </button>
              ))}
            </div>

            {/* Results Header */}
            <div className="search-results-header">
              <div>
                <h2 className="search-results-title">
                  {isBrowseMode ? 'Indexed Precedent Cases' : 'Search Results'}
                </h2>
                <p className="search-results-count">
                  {isBrowseMode
                    ? `Displaying ${results.length} Supreme Court case records from 105 indexed precedents`
                    : `Found ${results.length} result${results.length === 1 ? '' : 's'} for "${query}"`}
                </p>
              </div>

              <div className="search-sort-group">
                <span>Sort by:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="search-sort-select"
                >
                  <option value="relevance">Relevance</option>
                  <option value="date">Date (Newest)</option>
                  <option value="case_number">Case Number</option>
                </select>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="search-error-banner">
                <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="search-loading-box">
                <div className="search-spinner"></div>
                <p className="search-loading-text">
                  {query ? 'Retrieving vector embeddings from PostgreSQL pgvector...' : 'Loading indexed case records...'}
                </p>
              </div>
            )}

            {/* Results List */}
            {!loading && results.length > 0 && (
              <div className="search-results-list">
                {results.map((evidence, idx) => (
                  <EvidenceCard key={idx} evidence={evidence} />
                ))}
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && query && results.length === 0 && (
              <div className="search-empty-card">
                <FileSearch className="search-empty-icon" />
                <h3 className="search-empty-title">No Matching Case Records</h3>
                <p className="search-empty-desc">
                  No Supreme Court judgments closely matched &ldquo;{query}&rdquo;. Try broader terms like &ldquo;appeal&rdquo;, &ldquo;tax&rdquo;, &ldquo;accident&rdquo;, or click &ldquo;All Cases&rdquo; above.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
