import { Link } from 'react-router-dom';
import { Check, FileText, ExternalLink, ArrowRight } from 'lucide-react';

export default function EvidenceCard({ evidence }) {
  if (!evidence) return null;

  const {
    case_id,
    case_number,
    case_title,
    document_title,
    document_type,
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
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs hover:shadow-md transition space-y-3">
      {/* Top Header: Title & Score Badge */}
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
          <Link
            to={`/cases/${case_id}`}
            className="hover:text-blue-600 transition"
          >
            {case_title || 'Judicial Case Record'}
          </Link>
        </h3>

        {/* Score Pill matching Screen 2: green badge with check icon */}
        <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-semibold flex-shrink-0">
          <Check className="h-3.5 w-3.5 stroke-[2.5]" />
          <span>{formattedScore}</span>
        </div>
      </div>

      {/* Meta Row: Case Number | Court | Date */}
      <div className="text-xs text-slate-500 flex flex-wrap items-center gap-2">
        <span className="font-semibold text-slate-700">{case_number || '2023 INSC'}</span>
        <span>•</span>
        <span>Supreme Court of India</span>
        <span>•</span>
        <span>Verified Record</span>
      </div>

      {/* Snippet text */}
      {snippet && (
        <p className="text-sm text-slate-700 leading-relaxed font-serif text-slate-700/90 bg-slate-50/60 p-3 rounded-lg border-l-2 border-blue-500">
          {snippet.startsWith('...') ? snippet : `...${snippet}`}
        </p>
      )}

      {/* Footer: Page tag and Action links */}
      <div className="flex items-center justify-between pt-1 text-xs">
        <div className="flex items-center space-x-2">
          {page_number && (
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[11px] font-medium border border-slate-200">
              <FileText className="h-3 w-3 text-slate-400" />
              <span>Page {page_number}</span>
            </span>
          )}
          {document_title && (
            <span className="text-slate-400 text-[11px] truncate max-w-[200px] hidden sm:inline">
              {document_title}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-3">
          {source_url && (
            <a
              href={source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-500 hover:text-blue-600 flex items-center space-x-1 transition font-medium"
            >
              <span>PDF</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
          <Link
            to={`/cases/${case_id}`}
            className="text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1 transition"
          >
            <span>View Case</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}
