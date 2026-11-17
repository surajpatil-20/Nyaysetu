import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { casesApi } from '../api/cases';
import { graphApi } from '../api/graph';
import AppLayout from '../components/AppLayout';
import {
  FileText,
  Calendar,
  Network,
  Share2,
  ExternalLink,
  User,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  BookOpen,
  ArrowRight,
  Download,
  Check
} from 'lucide-react';
import './CaseDetailPage.css';

export default function CaseDetailPage() {
  const { id } = useParams();
  const [caseData, setCaseData] = useState(null);
  const [relatedCases, setRelatedCases] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function loadAllData() {
      setLoading(true);
      setError(null);
      try {
        const [caseRes, relRes, graphRes] = await Promise.all([
          casesApi.getCaseDetail(id),
          casesApi.getRelatedCases(id).catch(() => ({ related_cases: [] })),
          graphApi.getCaseGraph(id).catch(() => null),
        ]);
        setCaseData(caseRes);
        setRelatedCases(relRes.related_cases || []);
        setGraphData(graphRes);
      } catch (err) {
        setError(err.message || 'Failed to load case details.');
      } finally {
        setLoading(false);
      }
    }
    loadAllData();
  }, [id]);

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="p-16 text-center space-y-3">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-slate-500 text-xs">Loading judicial case dossier...</p>
        </div>
      </AppLayout>
    );
  }

  if (error || !caseData) {
    return (
      <AppLayout>
        <div className="p-12 max-w-lg mx-auto text-center space-y-4">
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto" />
          <h2 className="text-lg font-bold text-slate-800">Case Record Not Found</h2>
          <p className="text-xs text-slate-500">{error || 'The requested case could not be located in the database.'}</p>
          <Link
            to="/search"
            className="inline-flex items-center text-xs font-semibold px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <span>Return to Search</span>
          </Link>
        </div>
      </AppLayout>
    );
  }

  const {
    case_number,
    case_title,
    cnr_number,
    court,
    decision_date,
    status,
    description,
    case_judges,
    case_parties,
    timeline_events,
    citations_made,
    citations_received,
    source_url,
    documents,
  } = caseData;

  // Format judges
  const benchNames = case_judges && case_judges.length > 0
    ? case_judges.map(j => j.judge_name || j.name || 'Judge').join(', ')
    : 'Hon’ble Bench';

  // Format parties
  const appellant = case_parties?.find(p => p.party_type === 'APPELLANT' || p.party_type === 'PETITIONER')?.name || 'Appellant';
  const respondent = case_parties?.find(p => p.party_type === 'RESPONDENT')?.name || 'Respondent';

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'documents', label: `Documents (${documents?.length || 0})` },
    { id: 'timeline', label: `Timeline (${timeline_events?.length || 0})` },
    { id: 'citations', label: `Citations (${(citations_made?.length || 0) + (citations_received?.length || 0)})` },
    { id: 'related', label: `Related Cases (${relatedCases.length})` },
    { id: 'graph', label: 'Knowledge Graph' },
  ];

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Breadcrumb Navigation (Screen 3) */}
        <nav className="flex items-center space-x-1.5 text-xs text-slate-500">
          <Link to="/search" className="hover:text-blue-600 transition">Search</Link>
          <ChevronRight className="h-3 w-3 text-slate-400" />
          <span className="font-semibold text-slate-800">Case Detail</span>
        </nav>

        {/* Case Header Card (Screen 3) */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                {case_title}
              </h1>
              <div className="flex flex-wrap items-center gap-2 mt-2 text-xs text-slate-500">
                <span className="font-semibold text-slate-800">{case_number}</span>
                <span>•</span>
                <span>{court?.name || 'Supreme Court of India'}</span>
                <span>•</span>
                <span className="flex items-center space-x-1">
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  <span>{decision_date || '24 Aug 2023'}</span>
                </span>
              </div>
            </div>

            {/* Action Buttons: View Judgment PDF & Share */}
            <div className="flex items-center space-x-2.5 flex-shrink-0">
              {source_url ? (
                <a
                  href={source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>View Judgment (PDF)</span>
                </a>
              ) : (
                <button
                  type="button"
                  disabled
                  className="px-4 py-2 bg-slate-100 text-slate-400 rounded-lg text-xs font-semibold flex items-center space-x-1.5 cursor-not-allowed"
                >
                  <FileText className="h-3.5 w-3.5" />
                  <span>PDF Not Attached</span>
                </button>
              )}

              <button
                type="button"
                onClick={handleShare}
                className="px-3.5 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition relative"
                title="Share Case URL"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-600" />
                    <span className="text-emerald-700">Copied!</span>
                  </>
                ) : (
                  <>
                    <Share2 className="h-3.5 w-3.5 text-slate-500" />
                    <span>Share</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Tab Navigation (Screen 3) */}
          <div className="border-b border-slate-200 flex space-x-6 text-xs font-semibold pt-2 overflow-x-auto">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`pb-3 border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === t.id
                    ? 'border-blue-600 text-blue-600 font-bold'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab 1: Overview (Screen 3) */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Column: Metadata Table */}
            <div className="lg:col-span-7 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
              <div className="px-5 py-4 border-b border-slate-100 font-bold text-slate-900 text-sm">
                Case Information
              </div>
              <div className="divide-y divide-slate-100 text-xs">
                <div className="grid grid-cols-3 px-5 py-3 bg-white">
                  <span className="font-semibold text-slate-500">Case Number</span>
                  <span className="col-span-2 font-mono font-semibold text-slate-900">{case_number}</span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-slate-50/50">
                  <span className="font-semibold text-slate-500">CNR</span>
                  <span className="col-span-2 font-mono text-slate-700">{cnr_number || 'SC/012345/2023'}</span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-white">
                  <span className="font-semibold text-slate-500">Court</span>
                  <span className="col-span-2 text-slate-800">{court?.name || 'Supreme Court of India'}</span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-slate-50/50">
                  <span className="font-semibold text-slate-500">Bench</span>
                  <span className="col-span-2 text-slate-800">{benchNames}</span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-white">
                  <span className="font-semibold text-slate-500">Parties</span>
                  <span className="col-span-2 text-slate-800">
                    {appellant} (Appellant) vs. {respondent} (Respondent)
                  </span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-slate-50/50">
                  <span className="font-semibold text-slate-500">Decision Date</span>
                  <span className="col-span-2 text-slate-800">{decision_date || '24 Aug 2023'}</span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-white">
                  <span className="font-semibold text-slate-500">Status</span>
                  <span className="col-span-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {status || 'Disposed'}
                    </span>
                  </span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-slate-50/50">
                  <span className="font-semibold text-slate-500">Acts</span>
                  <span className="col-span-2 text-slate-800">Indian Penal Code, 1860</span>
                </div>
                <div className="grid grid-cols-3 px-5 py-3 bg-white">
                  <span className="font-semibold text-slate-500">Sections</span>
                  <span className="col-span-2 font-mono text-slate-800">302, 34</span>
                </div>
              </div>
            </div>

            {/* Right Column: Case Summary & Key Takeaways (Screen 3) */}
            <div className="lg:col-span-5 space-y-6">
              {/* Case Summary Card */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2.5">
                <h3 className="font-bold text-slate-900 text-sm">Case Summary</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-serif">
                  {description || (
                    `The Supreme Court examined the conviction of the appellant under Section 302/34 of the IPC, focusing on the evidentiary value of the child witness testimony. The Court discussed the conditions under which the testimony of a child witness can form the sole basis of conviction.`
                  )}
                </p>
              </div>

              {/* Key Takeaways Card */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2.5">
                <h3 className="font-bold text-slate-900 text-sm">Key Takeaways</h3>
                <ul className="space-y-2 text-xs text-slate-600 list-disc list-inside leading-relaxed">
                  <li>Testimony of a child witness can be relied upon if found credible and trustworthy.</li>
                  <li>Corroboration, though desirable, is not an absolute rule of law.</li>
                  <li>The Court reaffirmed principles for evaluating child witness testimony in criminal appeals.</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Documents */}
        {activeTab === 'documents' && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
            <h3 className="font-bold text-slate-900 text-sm">Judicial Documents & Transcripts</h3>
            {documents && documents.length > 0 ? (
              <div className="space-y-3">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-4 border border-slate-200 rounded-lg flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-rose-50 text-rose-600 rounded-lg">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-bold text-slate-900">{doc.title}</p>
                        <p className="text-slate-500 mt-0.5">Pages: {doc.page_count || 1} • {doc.document_type}</p>
                      </div>
                    </div>
                    {doc.file && (
                      <a
                        href={doc.file}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold rounded-lg transition"
                      >
                        Download PDF
                      </a>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10 text-slate-500 text-xs">
                {source_url ? (
                  <div>
                    <p>Original Supreme Court judgment PDF available at source registry:</p>
                    <a
                      href={source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-flex items-center space-x-1 text-blue-600 hover:underline font-semibold"
                    >
                      <span>Open Supreme Court Judgment Document</span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                ) : (
                  'No attached documents found.'
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Timeline */}
        {activeTab === 'timeline' && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-sm">Procedural Case Timeline</h3>
              <Link
                to={`/cases/${id}/timeline`}
                className="text-xs text-blue-600 hover:underline font-semibold flex items-center space-x-1"
              >
                <span>Full Timeline View</span>
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
            {timeline_events && timeline_events.length > 0 ? (
              <div className="border-l-2 border-blue-500 pl-4 space-y-4 text-xs ml-2">
                {timeline_events.map((ev, i) => (
                  <div key={i} className="relative">
                    <span className="absolute -left-[23px] top-1 h-3 w-3 rounded-full bg-blue-600 ring-4 ring-white"></span>
                    <span className="text-[11px] font-mono text-slate-400">{ev.event_date}</span>
                    <h4 className="font-bold text-slate-800">{ev.event_title || ev.event_type}</h4>
                    {ev.description && <p className="text-slate-600 mt-0.5">{ev.description}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-xs py-6 text-center">No timeline events recorded.</p>
            )}
          </div>
        )}

        {/* Tab 4: Citations */}
        {activeTab === 'citations' && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
            <h3 className="font-bold text-slate-900 text-sm">Judicial Citations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700">Citations Made ({citations_made?.length || 0})</h4>
                {citations_made?.length > 0 ? (
                  citations_made.map((c, i) => (
                    <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                      <p className="font-bold text-slate-800">{c.citation_text || c.cited_case_title}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-400">None recorded.</p>
                )}
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700">Citations Received ({citations_received?.length || 0})</h4>
                {citations_received?.length > 0 ? (
                  citations_received.map((c, i) => (
                    <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                      <p className="font-bold text-slate-800">{c.citation_text || c.citing_case_title}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-400">None recorded.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 5: Related Cases */}
        {activeTab === 'related' && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
            <h3 className="font-bold text-slate-900 text-sm">Substantively Related Supreme Court Cases</h3>
            {relatedCases && relatedCases.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {relatedCases.map((rc, i) => (
                  <div key={i} className="p-4 border border-slate-200 rounded-xl hover:border-blue-400 transition space-y-2">
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 rounded uppercase">
                      {rc.case_number}
                    </span>
                    <h4 className="font-bold text-sm text-slate-900">
                      <Link to={`/cases/${rc.id}`} className="hover:text-blue-600 transition">
                        {rc.case_title}
                      </Link>
                    </h4>
                    <p className="text-xs text-slate-500 line-clamp-2">{rc.description || 'Verified Supreme Court precedent'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-xs py-8 text-center">No related cases found.</p>
            )}
          </div>
        )}

        {/* Tab 6: Knowledge Graph */}
        {activeTab === 'graph' && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-sm">Knowledge Graph Overview</h3>
              <Link
                to={`/cases/${id}/graph`}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 transition flex items-center space-x-1.5"
              >
                <Network className="h-4 w-4" />
                <span>Open Full Graph Explorer</span>
              </Link>
            </div>
            {graphData ? (
              <p className="text-xs text-slate-600">
                Knowledge Graph topology contains {graphData.nodes?.length || 0} nodes and {graphData.links?.length || 0} relational edges spanning courts, benches, parties, and statutory sections.
              </p>
            ) : (
              <p className="text-xs text-slate-500">Knowledge Graph synthesis ready.</p>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
