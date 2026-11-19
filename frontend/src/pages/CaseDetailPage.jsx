import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { casesApi } from '../api/cases';
import { graphApi } from '../api/graph';
import AppLayout from '../components/AppLayout';
import {
  Calendar,
  Share2,
  ExternalLink,
  ChevronRight,
  Download,
  Check,
  FileText,
  Network,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { CaseDossierSkeleton } from '../components/Skeleton';
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
        <div className="case-detail-container">
          <CaseDossierSkeleton />
        </div>
      </AppLayout>
    );
  }

  if (error || !caseData) {
    return (
      <AppLayout>
        <div className="case-detail-container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto mb-3" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>Case Record Not Found</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>
            {error || 'The requested case could not be located in the database.'}
          </p>
          <Link
            to="/search"
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary-navy)',
              color: '#ffffff',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              fontSize: '0.8125rem',
              fontWeight: 600,
            }}
          >
            Return to Search
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
    case_type,
  } = caseData;

  // Format judges
  const benchNames = case_judges && case_judges.length > 0
    ? case_judges.map((j) => j.judge_name || j.name || 'Judge').join(', ')
    : 'Hon’ble Supreme Court Bench';

  // Format parties dynamically
  const appellant = case_parties?.find((p) => p.party_type === 'APPELLANT' || p.party_type === 'PETITIONER')?.party_name
    || case_parties?.find((p) => p.party_type === 'APPELLANT' || p.party_type === 'PETITIONER')?.name
    || case_parties?.[0]?.party_name
    || case_parties?.[0]?.name
    || 'Petitioner / Appellant';

  const respondent = case_parties?.find((p) => p.party_type === 'RESPONDENT')?.party_name
    || case_parties?.find((p) => p.party_type === 'RESPONDENT')?.name
    || case_parties?.[1]?.party_name
    || case_parties?.[1]?.name
    || 'Respondent';

  // Dynamic Case Summary & Fixture Handling
  const isDemoFixture = Boolean(
    description?.includes('[DEMO DATA') || caseData?.source_name === 'DEMO SOURCE'
  );
  const cleanDescription = description
    ? description.replace(/^\[DEMO DATA\s*[—–-]\s*NOT REAL JUDICIAL RECORD\]\s*/i, '').trim()
    : '';

  const summaryText = cleanDescription
    || `Precedent judgment delivered by the ${court?.name || 'Supreme Court of India'} in ${case_title} (${case_number}). Coram bench presided over by ${benchNames}. Final disposition status: ${status || 'Disposed'}.`;

  // Dynamic Takeaways
  const takeaways = [
    `Adjudicated by ${benchNames}.`,
    `Jurisdiction: ${court?.name || 'Supreme Court of India'} (${case_type || 'Appellate'}).`,
    `Procedural case disposition: ${status || 'Disposed'}.`,
    ...(decision_date ? [`Judgment pronounced on ${decision_date}.`] : []),
    ...(cleanDescription ? [`Evidentiary ratio: ${cleanDescription.slice(0, 160)}...`] : []),
  ];

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
      <div className="case-detail-container">
        {/* Breadcrumb Navigation (Screen 3) */}
        <nav className="case-detail-breadcrumb">
          <Link to="/search">Search</Link>
          <span className="separator">&gt;</span>
          <span className="current">Case Detail</span>
        </nav>

        {/* Notice for Early Test Fixture Cases */}
        {isDemoFixture && (
          <div style={{
            backgroundColor: 'var(--warning-bg)',
            border: '1px solid var(--warning-border)',
            borderRadius: 'var(--radius-md)',
            padding: '0.75rem 1rem',
            fontSize: '0.75rem',
            color: 'var(--warning-text)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}>
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>
              <strong>System Notice:</strong> This dossier ({case_number}) is an early development fixture. Official Supreme Court judgment precedents are indexed under verified citations (e.g., <Link to="/cases/105" style={{ textDecoration: 'underline', fontWeight: 700, color: 'inherit' }}>2023 INSC 599 — Pradeep v. State of Haryana</Link>).
            </span>
          </div>
        )}

        {/* Case Header Card (Screen 3) */}
        <div className="case-detail-header-card">
          <div className="case-detail-header-top">
            <div className="case-detail-title-group">
              <h1 className="case-detail-title">{case_title}</h1>
              <div className="case-detail-meta-pills">
                <span className="case-detail-num-badge">{case_number || 'Precedent Record'}</span>
                <span>•</span>
                <span>{court?.name || 'Supreme Court of India'}</span>
                <span>•</span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  <span>{decision_date || 'Pronounced Judgment'}</span>
                </span>
              </div>
            </div>

            {/* Action Buttons: View Judgment PDF & Share */}
            <div className="case-detail-header-actions">
              {source_url ? (
                <a
                  href={source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="case-detail-btn-pdf"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>View Judgment (PDF)</span>
                </a>
              ) : (
                <span className="case-detail-btn-disabled">
                  <FileText className="h-3.5 w-3.5" />
                  <span>Judgment PDF</span>
                </span>
              )}

              <button
                type="button"
                onClick={handleShare}
                className="case-detail-btn-share"
                title="Share Case URL"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-600" />
                    <span style={{ color: '#059669' }}>Copied</span>
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

          {/* Navigation Tabs (Screen 3) */}
          <div className="case-detail-tabs-bar">
            {tabs.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveTab(t.id)}
                className={`case-detail-tab-btn ${activeTab === t.id ? 'active' : ''}`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab 1: Overview (Screen 3 - 2 Column Layout) */}
        {activeTab === 'overview' && (
          <div className="case-detail-overview-grid">
            {/* Left Column: Case Information Card */}
            <div className="case-info-table-card">
              <div className="case-info-table-header">Case Information</div>
              <div>
                <div className="case-info-row">
                  <span className="case-info-label">Case Number</span>
                  <span className="case-info-val" style={{ fontFamily: 'monospace' }}>
                    {case_number || 'Precedent Record'}
                  </span>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">CNR</span>
                  <span className="case-info-val" style={{ fontFamily: 'monospace' }}>
                    {cnr_number || `INSC/${id}/RECORD`}
                  </span>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">Court</span>
                  <span className="case-info-val">{court?.name || 'Supreme Court of India'}</span>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">Bench</span>
                  <span className="case-info-val">{benchNames}</span>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">Parties</span>
                  <span className="case-info-val">
                    {appellant} (Petitioner/Appellant) vs. {respondent} (Respondent)
                  </span>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">Decision Date</span>
                  <span className="case-info-val">{decision_date || 'Pronounced'}</span>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">Status</span>
                  <div className="case-info-val">
                    <span className="case-info-status-pill">{status || 'Disposed'}</span>
                  </div>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">Case Type</span>
                  <span className="case-info-val">{case_type || 'Appellate Precedent Jurisdiction'}</span>
                </div>
                <div className="case-info-row">
                  <span className="case-info-label">Registry Source</span>
                  <span className="case-info-val">
                    {caseData.source_name || 'Indian Supreme Court Open Dataset (AWS)'}
                  </span>
                </div>
              </div>
            </div>

            {/* Right Column: Case Summary & Key Takeaways */}
            <div className="case-side-column">
              {/* Case Summary Card */}
              <div className="case-summary-card">
                <h3 className="case-card-heading">Case Summary</h3>
                <p className="case-summary-text">
                  {summaryText}
                </p>
              </div>

              {/* Key Takeaways Card */}
              <div className="case-summary-card">
                <h3 className="case-card-heading">Key Takeaways</h3>
                <ul className="case-takeaways-list">
                  {takeaways.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Documents */}
        {activeTab === 'documents' && (
          <div className="case-tab-content-card">
            <h3 className="case-card-heading">Judicial Documents &amp; Transcripts</h3>
            {documents && documents.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {documents.map((doc) => (
                  <div key={doc.id} className="case-doc-item">
                    <div className="case-doc-info">
                      <div className="case-doc-icon">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="case-doc-title">{doc.title}</p>
                        <p className="case-doc-meta">
                          Pages: {doc.page_count || 1} • {doc.document_type || 'Judicial Record'}
                        </p>
                      </div>
                    </div>
                    {doc.file && (
                      <a
                        href={doc.file}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="case-doc-download-btn"
                      >
                        Download PDF
                      </a>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                {source_url ? (
                  <div>
                    <p style={{ margin: 0 }}>Original Supreme Court judgment PDF available at source registry:</p>
                    <a
                      href={source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        marginTop: '0.5rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        color: 'var(--primary-navy)',
                        fontWeight: 600,
                        textDecoration: 'none',
                      }}
                    >
                      <span>Open Supreme Court Judgment Document</span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                ) : (
                  'No attached documents found for this precedent.'
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Timeline */}
        {activeTab === 'timeline' && (
          <div className="case-tab-content-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 className="case-card-heading">Procedural Case Timeline</h3>
              <Link
                to={`/cases/${id}/timeline`}
                style={{
                  fontSize: '0.75rem',
                  color: 'var(--primary-navy)',
                  fontWeight: 600,
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                }}
              >
                <span>Full Timeline View</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
            {timeline_events && timeline_events.length > 0 ? (
              <div style={{ borderLeft: '2px solid var(--primary-navy)', paddingLeft: '1rem', marginLeft: '0.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {timeline_events.map((ev, i) => (
                  <div key={i} style={{ position: 'relative' }}>
                    <div style={{ position: 'absolute', left: '-1.375rem', top: '0.25rem', width: '0.75rem', height: '0.75rem', borderRadius: '50%', backgroundColor: 'var(--accent-gold)', border: '2px solid #ffffff' }} />
                    <span style={{ fontSize: '0.6875rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>{ev.event_date}</span>
                    <h4 style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--text-primary)', margin: '0.125rem 0' }}>{ev.event_title || ev.event_type}</h4>
                    {ev.description && <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0 }}>{ev.description}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                Decision pronounced on {decision_date || 'record'}. Additional interlocutory orders not individually indexed.
              </p>
            )}
          </div>
        )}

        {/* Tab 4: Citations */}
        {activeTab === 'citations' && (
          <div className="case-tab-content-card">
            <h3 className="case-card-heading">Judicial Citations</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
              <div>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                  Citations Made ({citations_made?.length || 0})
                </h4>
                {citations_made?.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {citations_made.map((c, i) => (
                      <div key={i} style={{ padding: '0.75rem', backgroundColor: '#f8fafc', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                        <p style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{c.citation_text || c.cited_case_title}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>No citations made recorded.</p>
                )}
              </div>

              <div>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                  Citations Received ({citations_received?.length || 0})
                </h4>
                {citations_received?.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {citations_received.map((c, i) => (
                      <div key={i} style={{ padding: '0.75rem', backgroundColor: '#f8fafc', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                        <p style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{c.citation_text || c.citing_case_title}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>No citing precedents recorded.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 5: Related Cases */}
        {activeTab === 'related' && (
          <div className="case-tab-content-card">
            <h3 className="case-card-heading">Substantively Related Supreme Court Cases</h3>
            {relatedCases && relatedCases.length > 0 ? (
              <div className="case-related-grid">
                {relatedCases.map((rc, i) => (
                  <div key={i} className="case-related-card">
                    <span className="case-related-docket">{rc.case_number}</span>
                    <h4 className="case-related-title">
                      <Link to={`/cases/${rc.id}`}>{rc.case_title}</Link>
                    </h4>
                    <p className="case-related-desc">{rc.description || 'Verified Supreme Court precedent'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                No substantively linked companion cases indexed in current phase.
              </p>
            )}
          </div>
        )}

        {/* Tab 6: Knowledge Graph */}
        {activeTab === 'graph' && (
          <div className="case-tab-content-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h3 className="case-card-heading">Knowledge Graph Overview</h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  {graphData
                    ? `Knowledge Graph contains ${graphData.nodes?.length || 0} relational nodes and ${graphData.links?.length || 0} edges for this specific precedent.`
                    : 'Relational knowledge graph topology ready for exploration.'}
                </p>
              </div>
              <Link
                to={`/cases/${id}/graph`}
                className="case-detail-btn-pdf"
              >
                <Network className="h-4 w-4" />
                <span>Open Interactive Graph Explorer</span>
              </Link>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
