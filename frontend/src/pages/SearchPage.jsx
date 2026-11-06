import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchApi } from '../api/search';
import EvidenceCard from '../components/EvidenceCard';
import AppLayout from '../components/AppLayout';
import {
  Search,
  RotateCcw,
  SlidersHorizontal,
  ChevronDown,
  AlertCircle,
  FileSearch
} from 'lucide-react';

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
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Filters Card (Screen 2) */}
          <div className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
                <SlidersHorizontal className="h-4 w-4 text-blue-600" />
                <span>Filters</span>
              </h3>
              <button
                type="button"
                onClick={handleResetFilters}
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1"
              >
                <RotateCcw className="h-3 w-3" />
                <span>Reset</span>
              </button>
            </div>

            {/* Filter Form */}
            <div className="space-y-4 text-xs">
              {/* Court */}
              <div className="space-y-1.5">
                <label className="font-medium text-slate-700">Court</label>
                <select
                  value={court}
                  onChange={(e) => setCourt(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="Supreme Court of India">Supreme Court of India</option>
                  <option value="High Court of Delhi">High Court of Delhi</option>
                  <option value="High Court of Bombay">High Court of Bombay</option>
                </select>
              </div>

              {/* Year Range */}
              <div className="space-y-1.5">
                <label className="font-medium text-slate-700">Year</label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    value={startYear}
                    onChange={(e) => setStartYear(e.target.value)}
                    placeholder="1950"
                    min="1950"
                    max="2026"
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <input
                    type="number"
                    value={endYear}
                    onChange={(e) => setEndYear(e.target.value)}
                    placeholder="2024"
                    min="1950"
                    max="2026"
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Judge */}
              <div className="space-y-1.5">
                <label className="font-medium text-slate-700">Judge</label>
                <select
                  value={judge}
                  onChange={(e) => setJudge(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Select Judge</option>
                  <option value="A.S. Bopanna">Justice A.S. Bopanna</option>
                  <option value="Prashant Kumar Mishra">Justice Prashant Kumar Mishra</option>
                  <option value="D.Y. Chandrachud">Chief Justice D.Y. Chandrachud</option>
                </select>
              </div>

              {/* Act */}
              <div className="space-y-1.5">
                <label className="font-medium text-slate-700">Act</label>
                <select
                  value={act}
                  onChange={(e) => setAct(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Select Act</option>
                  <option value="Indian Penal Code, 1860">Indian Penal Code, 1860</option>
                  <option value="Code of Criminal Procedure, 1973">Code of Criminal Procedure, 1973</option>
                  <option value="Constitution of India">Constitution of India</option>
                  <option value="Indian Evidence Act, 1872">Indian Evidence Act, 1872</option>
                </select>
              </div>

              {/* Section */}
              <div className="space-y-1.5">
                <label className="font-medium text-slate-700">Section</label>
                <select
                  value={section}
                  onChange={(e) => setSection(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-xs transition mt-2"
              >
                Apply Filters
              </button>
            </div>
          </div>

          {/* Right Column: Search Input & Results (Screen 2) */}
          <div className="lg:col-span-8 space-y-5">
            {/* Search Input Bar */}
            <form onSubmit={handleSubmit} className="w-full">
              <div className="flex rounded-xl shadow-xs border border-slate-300 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 overflow-hidden bg-white">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="child witness testimony in Pradeep v State of Haryana"
                  className="flex-1 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-5 flex items-center justify-center transition disabled:opacity-50"
                  title="Search"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </form>

            {/* Results Header */}
            <div className="flex items-center justify-between pt-1">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Search Results</h2>
                {query && (
                  <p className="text-xs text-slate-500 mt-0.5">
                    Found {results.length} results for &ldquo;<span className="font-semibold text-slate-700">{query}</span>&rdquo;
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-500">Sort by:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 font-medium focus:outline-none"
                >
                  <option value="relevance">Relevance</option>
                  <option value="score">Score (High to Low)</option>
                  <option value="date">Date (Newest)</option>
                </select>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 text-xs flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-rose-600 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="py-16 text-center space-y-3">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="text-xs text-slate-500">Retrieving vector embeddings from PostgreSQL pgvector...</p>
              </div>
            )}

            {/* Results List */}
            {!loading && results.length > 0 && (
              <div className="space-y-4">
                {results.map((evidence, idx) => (
                  <EvidenceCard key={idx} evidence={evidence} />
                ))}
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && query && results.length === 0 && (
              <div className="bg-white border border-slate-200 rounded-xl p-12 text-center space-y-3">
                <FileSearch className="h-10 w-10 text-slate-400 mx-auto" />
                <h3 className="font-bold text-slate-800 text-base">No Matching Case Records</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  No Supreme Court judgments closely matched your semantic query. Try broadening your keywords or resetting filters.
                </p>
              </div>
            )}

            {/* Initial State */}
            {!loading && !query && (
              <div className="bg-white border border-slate-200 rounded-xl p-12 text-center space-y-3">
                <Search className="h-10 w-10 text-blue-500 mx-auto opacity-70" />
                <h3 className="font-bold text-slate-800 text-base">Begin Your Legal Research</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
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
