import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchApi } from '../api/search';
import EvidenceCard from '../components/EvidenceCard';
import AppLayout from '../components/AppLayout';
import {
  Search,
  RotateCcw,
  SlidersHorizontal,
  AlertCircle,
  FileSearch
} from 'lucide-react';
import './SearchPage.css';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';

  const [query, setQuery] = useState(queryParam);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filters matching Screen 2
  const [court, setCourt] = useState('Supreme Court of India');
  const [startYear, setStartYear] = useState('1950');
  const [endYear, setEndYear] = useState('2024');
  const [judge, setJudge] = useState('');
  const [act, setAct] = useState('');
  const [section, setSection] = useState('');
  const [sortBy, setSortBy] = useState('relevance');

  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await searchApi.hybridSearch({
        q: searchQuery,
        year: endYear !== '2024' || startYear !== '1950' ? endYear : undefined,
        alpha: 0.5,
        top_k: 20,
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
    }
  }, [queryParam]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query.trim() });
      performSearch(query.trim());
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
                </select>
              </div>

              {/* Year Range */}
              <div className="search-filter-group">
                <label className="search-filter-label">Year</label>
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
                <label className="search-filter-label">Judge</label>
                <select
                  value={judge}
                  onChange={(e) => setJudge(e.target.value)}
                  className="search-filter-select"
                >
                  <option value="">Select Judge</option>
                  <option value="A.S. Bopanna">Justice A.S. Bopanna</option>
                  <option value="Prashant Kumar Mishra">Justice Prashant Kumar Mishra</option>
                  <option value="D.Y. Chandrachud">Chief Justice D.Y. Chandrachud</option>
                </select>
              </div>

              {/* Act */}
              <div className="search-filter-group">
                <label className="search-filter-label">Act</label>
                <select
                  value={act}
                  onChange={(e) => setAct(e.target.value)}
                  className="search-filter-select"
                >
                  <option value="">Select Act</option>
                  <option value="Indian Penal Code, 1860">Indian Penal Code, 1860</option>
                  <option value="Code of Criminal Procedure, 1973">Code of Criminal Procedure, 1973</option>
                  <option value="Constitution of India">Constitution of India</option>
                  <option value="Indian Evidence Act, 1872">Indian Evidence Act, 1872</option>
                </select>
              </div>

              {/* Section */}
              <div className="search-filter-group">
                <label className="search-filter-label">Section</label>
                <select
                  value={section}
                  onChange={(e) => setSection(e.target.value)}
                  className="search-filter-select"
                >
                  <option value="">Select Section</option>
                  <option value="Section 302">Section 302</option>
                  <option value="Section 34">Section 34</option>
                  <option value="Section 438">Section 438</option>
                  <option value="Article 21">Article 21</option>
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
                  placeholder="child witness testimony in Pradeep v State of Haryana"
                  className="search-bar-input"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="search-bar-submit"
                  title="Search"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </form>

            {/* Results Header */}
            <div className="search-results-header">
              <div>
                <h2 className="search-results-title">Search Results</h2>
                {query && (
                  <p className="search-results-count">
                    Found {results.length} results for &ldquo;<strong>{query}</strong>&rdquo;
                  </p>
                )}
              </div>

              <div className="search-sort-group">
                <span>Sort by:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="search-sort-select"
                >
                  <option value="relevance">Relevance</option>
                  <option value="score">Score (High to Low)</option>
                  <option value="date">Date (Newest)</option>
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
                <p className="search-loading-text">Retrieving vector embeddings from PostgreSQL pgvector...</p>
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
                  No Supreme Court judgments closely matched your semantic query. Try broadening your keywords or resetting filters.
                </p>
              </div>
            )}

            {/* Initial State */}
            {!loading && !query && (
              <div className="search-empty-card">
                <Search className="search-empty-icon text-blue-500" />
                <h3 className="search-empty-title">Begin Your Legal Research</h3>
                <p className="search-empty-desc">
                  Type legal concepts or case names above to perform hybrid BM25 and pgvector cosine similarity search across 2,058 indexed document chunks.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
