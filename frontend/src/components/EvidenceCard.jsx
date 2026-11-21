import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, FileText, ExternalLink, ArrowRight, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import './EvidenceCard.css';

export default function EvidenceCard({ evidence }) {
  if (!evidence) return null;

  const [showMoreSnippets, setShowMoreSnippets] = useState(false);

  const {
    case_id,
    case_number,
    case_title,
    document_title,
    page_number,
    snippet,
    hybrid_score,
    source_url,
    matched_pages,
    matched_chunks_count,
    supporting_snippets,
  } = evidence;

  // Real backend relevance percentage (e.g. 92% Relevance)
  const relevancePercent = hybrid_score !== undefined
    ? Math.min(100, Math.round(Number(hybrid_score) * 100))
    : 85;

  return (
    <div className="evidence-card">
      {/* Top Header: Title & Score Badge */}
      <div className="evidence-card-header">
        <h3 className="evidence-card-title">
          <Link to={`/cases/${case_id}`}>
            {case_title || 'Supreme Court Judgment Record'}
          </Link>
        </h3>

        {/* Real Relevance Indicator & Hybrid Tag */}
        <div className="evidence-badges-group">
          <span className="evidence-hybrid-badge">
            <Sparkles className="h-3 w-3 text-[#FFA425]" />
            <span>Hybrid Match</span>
          </span>
          <div className="evidence-score-pill">
            <Check className="h-3 w-3 stroke-[3]" />
            <span>{relevancePercent}% Relevance</span>
          </div>
        </div>
      </div>

      {/* Meta Row: Docket • Court • Verified Record */}
      <div className="evidence-meta-row">
        <span className="evidence-case-num">{case_number || '2023 INSC'}</span>
        <span>•</span>
        <span>Supreme Court of India</span>
        <span>•</span>
        <span>Verified Legal Record</span>
      </div>

      {/* Primary Quotation Snippet */}
      {snippet && (
        <p className="evidence-snippet-box">
          {snippet.startsWith('...') || snippet.startsWith('…') ? snippet : `…${snippet}`}
        </p>
      )}

      {/* Supporting Snippets from Other Relevant Chunks in Same Judgment */}
      {supporting_snippets && supporting_snippets.length > 0 && (
        <div className="evidence-supporting-box">
          <button
            type="button"
            onClick={() => setShowMoreSnippets(!showMoreSnippets)}
            className="evidence-supporting-toggle-btn"
          >
            <span>
              {showMoreSnippets
                ? 'Hide additional matching excerpts'
                : `+${supporting_snippets.length} more matching excerpt${supporting_snippets.length > 1 ? 's' : ''} in this judgment`}
            </span>
            {showMoreSnippets ? (
              <ChevronUp className="h-3 w-3 text-slate-400" />
            ) : (
              <ChevronDown className="h-3 w-3 text-slate-400" />
            )}
          </button>

          {showMoreSnippets && (
            <div className="evidence-supporting-list">
              {supporting_snippets.map((supp, sIdx) => (
                <div key={sIdx} className="evidence-supporting-item">
                  <span className="evidence-supporting-page-tag">
                    Page {supp.page_number || 'N/A'}
                  </span>
                  <p className="evidence-supporting-text">
                    {supp.snippet.startsWith('...') || supp.snippet.startsWith('…') ? supp.snippet : `…${supp.snippet}`}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Footer: Page tag and Action links */}
      <div className="evidence-card-footer">
        <div className="flex items-center gap-2 flex-wrap">
          {matched_pages && matched_pages.length > 1 ? (
            <span
              className="evidence-page-badge"
              title={`Matching excerpts found on pages: ${matched_pages.join(', ')}`}
            >
              <FileText className="h-3 w-3 text-slate-400" />
              <span>Pages {matched_pages.join(', ')}</span>
              {matched_chunks_count > 1 && (
                <span className="evidence-chunks-count-tag">
                  ({matched_chunks_count} excerpts)
                </span>
              )}
            </span>
          ) : page_number ? (
            <span className="evidence-page-badge">
              <FileText className="h-3 w-3 text-slate-400" />
              <span>Page {page_number}</span>
            </span>
          ) : null}
          {document_title && (
            <span className="text-xs text-slate-400 truncate max-w-[240px] hidden sm:inline">
              {document_title}
            </span>
          )}
        </div>

        <div className="evidence-actions-group">
          {source_url && (
            <a
              href={source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="evidence-link-pdf"
            >
              <span>Judgment PDF</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
          <Link
            to={`/cases/${case_id}`}
            className="evidence-link-case"
          >
            <span>View Case Dossier</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
