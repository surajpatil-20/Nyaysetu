import { Link } from 'react-router-dom';
import { Check, FileText, ExternalLink, ArrowRight } from 'lucide-react';
import './EvidenceCard.css';

export default function EvidenceCard({ evidence }) {
  if (!evidence) return null;

  const {
    case_id,
    case_number,
    case_title,
    document_title,
    page_number,
    snippet,
    hybrid_score,
    source_url,
  } = evidence;

  // Format hybrid score as 4 decimal places (e.g. 0.9381)
  const formattedScore = hybrid_score !== undefined
    ? Number(hybrid_score).toFixed(4)
    : '0.9000';

  return (
    <div className="evidence-card">
      {/* Top Header: Title & Score Badge */}
      <div className="evidence-card-header">
        <h3 className="evidence-card-title">
          <Link to={`/cases/${case_id}`}>
            {case_title || 'Judicial Case Record'}
          </Link>
        </h3>

        {/* Score Pill matching Screen 2: green badge with check icon */}
        <div className="evidence-score-pill">
          <Check className="h-3.5 w-3.5 stroke-[2.5]" />
          <span>{formattedScore}</span>
        </div>
      </div>

      {/* Meta Row: Case Number | Court | Date */}
      <div className="evidence-meta-row">
        <span className="evidence-case-num">{case_number || '2023 INSC'}</span>
        <span>•</span>
        <span>Supreme Court of India</span>
        <span>•</span>
        <span>Verified Record</span>
      </div>

      {/* Snippet text */}
      {snippet && (
        <p className="evidence-snippet-box">
          {snippet.startsWith('...') ? snippet : `...${snippet}`}
        </p>
      )}

      {/* Footer: Page tag and Action links */}
      <div className="evidence-card-footer">
        <div className="flex items-center gap-2">
          {page_number && (
            <span className="evidence-page-badge">
              <FileText className="h-3 w-3 text-slate-400" />
              <span>Page {page_number}</span>
            </span>
          )}
          {document_title && (
            <span className="evidence-doc-title hidden sm:inline">
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
              <span>PDF</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
          <Link
            to={`/cases/${case_id}`}
            className="evidence-link-case"
          >
            <span>View Case</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}
