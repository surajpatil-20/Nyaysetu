import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { assistantApi } from '../api/assistant';
import AppLayout from '../components/AppLayout';
import {
  Scale,
  Send,
  FileText,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Sparkles,
  BookOpen,
  ArrowRight
} from 'lucide-react';

const QUICK_PROMPTS = [
  'What was held regarding child witness testimony in Pradeep v State of Haryana?',
  'Competency of child witness under Section 118 Evidence Act',
  'Principles of natural justice in S. Narahari v S.R. Kumar',
  'Standard of proof in criminal appeals in Union of India v Munshi Ram',
];

/**
 * Custom renderer for structured judicial markdown with interactive citation pills.
 */
function FormattedJudicialText({ content, onCitationClick }) {
  if (!content) return null;

  // Split into lines
  const lines = content.split('\n');

  const renderInline = (text) => {
    // Regex for [Evidence N]
    const parts = text.split(/(\[Evidence \d+\]|\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      const evMatch = part.match(/\[Evidence (\d+)\]/);
      if (evMatch) {
        const evIdx = parseInt(evMatch[1], 10);
        return (
          <button
            key={i}
            type="button"
            onClick={() => onCitationClick?.(evIdx)}
            className="inline-flex items-center px-1.5 py-0.5 mx-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 hover:text-blue-900 border border-blue-200 transition shadow-2xs"
            title={`Jump to Evidence ${evIdx}`}
          >
            {part}
          </button>
        );
      }
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="space-y-2 text-xs sm:text-sm text-slate-800 leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-1" />;

        // Heading 3
        if (trimmed.startsWith('### ')) {
          return (
            <h3 key={idx} className="text-xs sm:text-sm font-bold text-slate-900 pt-2 pb-0.5 border-b border-slate-100 flex items-center space-x-1.5">
              <span>{trimmed.replace('### ', '')}</span>
            </h3>
          );
        }

        // Blockquote
        if (trimmed.startsWith('> ')) {
          return (
            <blockquote
              key={idx}
              className="border-l-3 border-blue-600 bg-blue-50/60 pl-3.5 py-2 my-2 text-xs italic text-slate-700 rounded-r-md"
            >
              {renderInline(trimmed.replace(/^>\s*/, ''))}
            </blockquote>
          );
        }

        // Bullet list
        if (trimmed.startsWith('- ')) {
          return (
            <div key={idx} className="flex items-start space-x-2 pl-1 py-0.5">
              <span className="text-blue-600 font-bold mt-1 text-xs">•</span>
              <div className="flex-1">{renderInline(trimmed.replace(/^- \s*/, ''))}</div>
            </div>
          );
        }

        // Normal paragraph
        return <p key={idx}>{renderInline(trimmed)}</p>;
      })}
    </div>
  );
}

export default function AssistantPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'user',
      content: 'What was held regarding child witness testimony in Pradeep v State of Haryana?',
    },
    {
      role: 'assistant',
      content:
        '### Executive Judicial Holding\nIn **PRADEEP versus THE STATE OF HARYANA (2023 INSC 599)** [Evidence 1], the Supreme Court of India (Bench of Hon\'ble Justice Abhay S. Oka) held that the uncorroborated testimony of a child witness cannot form the sole basis of conviction where the preliminary examination is inadequate and the possibility of tutoring cannot be ruled out.\n\n### Key Legal Principles & Ratio Decidendi\n- **Witness Competency [Evidence 2] (Page 7)**: Under Section 118 of the Evidence Act, 1872, a child witness is competent to depose unless the court considers that he is prevented from understanding questions or giving rational answers due to tender years.\n- **Standard of Corroboration & Risk of Tutoring [Evidence 3, 4] (Pages 8, 11)**: Corroboration of the testimony of a child witness is not an absolute rule of law, but a measure of caution and prudence because a child of tender age is easily susceptible to tutoring.\n\n### Statutory Provisions Examined\n- **Enactments**: Indian Evidence Act, 1872, Indian Penal Code, 1860, Oaths Act, 1969\n- **Sections / Articles**: Section 118, Section 302 r/w s.34, Section 449, 324, Section 4\n\n### Procedural Record & Disposition\n- **Order of the Court [Evidence 1, 4]**: The conviction under Section 302/34 IPC was set aside, granting the benefit of doubt; the appeal was allowed and the appellant was acquitted.',
      evidenceCount: 5,
      evidence: [
        {
          citation_tag: '[Evidence 1]',
          case_id: 1,
          case_title: 'PRADEEP versus THE STATE OF HARYANA (2023 INSC 599)',
          case_number: '2023 INSC 599',
          page_number: 1,
          court_name: 'Supreme Court of India',
          bench: 'ABHAY S. OKA',
          snippet:
            'Evidence – Testimony of child witness – Sole basis of conviction – When not proper – Appellant along with co-accused was convicted for offences u/s. 302 r/w s.34, IPC based on testimony of PW-1, minor son of the deceased...',
          source_url: 'https://indian-supreme-court-judgments.s3.amazonaws.com/2023/INSC_599.pdf',
        },
        {
          citation_tag: '[Evidence 2]',
          case_id: 1,
          case_title: 'PRADEEP versus THE STATE OF HARYANA (2023 INSC 599)',
          case_number: '2023 INSC 599',
          page_number: 7,
          court_name: 'Supreme Court of India',
          bench: 'ABHAY S. OKA',
          snippet:
            'Under Section 118 of the Evidence Act, 1872, a child witness is competent to depose unless the Court considers that he is prevented from understanding the questions put to him, or from giving rational answers by the reason of tender age...',
          source_url: 'https://indian-supreme-court-judgments.s3.amazonaws.com/2023/INSC_599.pdf',
        },
        {
          citation_tag: '[Evidence 3]',
          case_id: 1,
          case_title: 'PRADEEP versus THE STATE OF HARYANA (2023 INSC 599)',
          case_number: '2023 INSC 599',
          page_number: 8,
          court_name: 'Supreme Court of India',
          bench: 'ABHAY S. OKA',
          snippet:
            'It is a well-settled principle that corroboration of the testimony of a child witness is not a rule but a measure of caution and prudence. A child witness of tender age is easily susceptible to tutoring...',
          source_url: 'https://indian-supreme-court-judgments.s3.amazonaws.com/2023/INSC_599.pdf',
        },
      ],
      showEvidence: true,
    },
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (userPrompt) => {
    const promptToSend = userPrompt || query;
    if (!promptToSend.trim() || loading) return;

    const userMessage = { role: 'user', content: promptToSend };
    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await assistantApi.askAssistant({
        query: promptToSend,
        top_k: 5,
        alpha: 0.5,
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        hasSufficientEvidence: response.has_sufficient_evidence ?? true,
        insufficientEvidenceReason: response.insufficient_evidence_reason,
        evidence: response.sources || response.evidence || [],
        evidenceCount: (response.sources || response.evidence || []).length || 0,
        showEvidence: true,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'An error occurred while retrieving judicial evidence: ' +
            (err.message || 'Please verify your session and try again.'),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleEvidence = (index) => {
    setMessages((prev) =>
      prev.map((msg, i) =>
        i === index ? { ...msg, showEvidence: !msg.showEvidence } : msg
      )
    );
  };

  return (
    <AppLayout>
      <div className="p-4 sm:p-6 max-w-5xl mx-auto space-y-4 flex flex-col h-[calc(100vh-64px)]">
        {/* Header (Panel 5 in Figma design) */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-200/80 pb-3">
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                Judicial AI Assistant
              </h1>
              <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-bold rounded-full uppercase tracking-wider">
                Evidence-Grounded RAG
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Ask questions about judicial cases, legal principles, statutory provisions, or specific Supreme Court judgments.
            </p>
          </div>
        </div>

        {/* Quick starter chips */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none text-xs">
          <span className="text-[11px] font-semibold text-slate-500 flex items-center space-x-1 shrink-0">
            <Sparkles className="h-3 w-3 text-amber-500" />
            <span>Suggested:</span>
          </span>
          {QUICK_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              disabled={loading}
              onClick={() => handleSend(prompt)}
              className="shrink-0 px-2.5 py-1 bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-300 rounded-full text-slate-700 hover:text-blue-700 text-[11px] font-medium transition shadow-2xs disabled:opacity-50"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Conversation Stream */}
        <div className="flex-1 bg-white border border-slate-200 rounded-xl p-4 sm:p-5 overflow-y-auto space-y-6 shadow-xs">
          {messages.map((msg, index) => {
            if (msg.role === 'user') {
              return (
                <div key={index} className="flex justify-end">
                  <div className="bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-2.5 max-w-xl text-xs sm:text-sm font-medium leading-relaxed shadow-xs">
                    {msg.content}
                  </div>
                </div>
              );
            }

            // Assistant Message
            return (
              <div key={index} className="flex items-start space-x-3 max-w-3xl">
                <div className="h-8 w-8 rounded-full bg-[#0A192F] text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                  <Scale className="h-4 w-4 text-blue-400" />
                </div>

                <div className="space-y-3 flex-1 min-w-0">
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 sm:p-5 shadow-2xs">
                    <FormattedJudicialText content={msg.content} />

                    {/* Insufficient Evidence Safeguard */}
                    {msg.hasSufficientEvidence === false && (
                      <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-start space-x-2">
                        <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                        <span>{msg.insufficientEvidenceReason || 'Insufficient judicial evidence found for this inquiry in the NYAYASETU repository.'}</span>
                      </div>
                    )}
                  </div>

                  {/* Expandable Evidence Container (Screen 5) */}
                  {msg.evidence && msg.evidence.length > 0 && (
                    <div className="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden shadow-2xs">
                      <button
                        type="button"
                        onClick={() => toggleEvidence(index)}
                        className="w-full px-4 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-700 hover:bg-slate-100 transition"
                      >
                        <span className="flex items-center space-x-1.5">
                          <BookOpen className="h-3.5 w-3.5 text-blue-600" />
                          <span>Grounded Evidence Citations ({msg.evidenceCount || msg.evidence.length})</span>
                        </span>
                        {msg.showEvidence ? (
                          <ChevronUp className="h-4 w-4 text-slate-400" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-slate-400" />
                        )}
                      </button>

                      {msg.showEvidence && (
                        <div className="px-4 pb-4 pt-1 space-y-3 border-t border-slate-200/60 divide-y divide-slate-200/50">
                          {msg.evidence.map((ev, evIdx) => (
                            <div key={evIdx} className="pt-3 first:pt-1 space-y-2 text-xs">
                              <div className="flex flex-wrap items-center justify-between gap-1.5">
                                <div className="flex items-center space-x-2 min-w-0">
                                  <div className="p-1 bg-rose-100 text-rose-600 rounded">
                                    <FileText className="h-3.5 w-3.5" />
                                  </div>
                                  <span className="font-bold text-slate-900 truncate">
                                    {ev.citation_tag ? `${ev.citation_tag} ` : ''}
                                    {ev.case_title || ev.case_number || 'Supreme Court Record'}
                                  </span>
                                </div>
                                <div className="flex items-center space-x-1.5 shrink-0">
                                  {ev.court_name && (
                                    <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-medium">
                                      {ev.court_name}
                                    </span>
                                  )}
                                  {ev.page_number && (
                                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-[10px] font-bold">
                                      Page {ev.page_number}
                                    </span>
                                  )}
                                </div>
                              </div>

                              {ev.bench && (
                                <p className="text-[11px] text-slate-500">
                                  <span className="font-semibold text-slate-600">Coram:</span> {ev.bench}
                                </p>
                              )}

                              <p className="text-slate-700 font-serif italic text-xs leading-relaxed bg-white p-3 rounded-lg border border-slate-200/70 shadow-2xs">
                                &ldquo;{ev.snippet}&rdquo;
                              </p>

                              <div className="flex items-center justify-between pt-1">
                                {ev.case_id ? (
                                  <Link
                                    to={`/cases/${ev.case_id}`}
                                    className="text-[11px] text-slate-600 hover:text-blue-600 flex items-center space-x-1 font-medium transition"
                                  >
                                    <span>View Case Dossier</span>
                                    <ArrowRight className="h-3 w-3" />
                                  </Link>
                                ) : <div />}

                                <a
                                  href={ev.source_url || 'https://registry.opendata.aws/indian-supreme-court-judgments/'}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-[11px] text-blue-600 hover:text-blue-800 flex items-center space-x-1 font-semibold"
                                >
                                  <span>View Source (AWS Open Data)</span>
                                  <ExternalLink className="h-3 w-3" />
                                </a>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex items-start space-x-3 text-slate-500 text-xs py-2">
              <div className="h-8 w-8 rounded-full bg-[#0A192F] text-white flex items-center justify-center shrink-0">
                <Scale className="h-4 w-4 text-blue-400" />
              </div>
              <div className="flex items-center space-x-2 bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-2xs">
                <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce"></div>
                <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.2s]"></div>
                <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.4s]"></div>
                <span className="ml-2 text-slate-700 font-medium">Retrieving grounded judicial citations & synthesizing holding...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar & Disclaimer (Panel 5 in Figma design) */}
        <div className="space-y-2">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center rounded-xl bg-white border border-slate-300 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 shadow-xs overflow-hidden"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about cases, legal principles, or judgments..."
              className="flex-1 px-4 py-3.5 text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3.5 flex items-center justify-center transition disabled:opacity-50 cursor-pointer"
              title="Send Message"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>

          {/* Legal Disclaimer matching Figma Panel 5 bottom */}
          <p className="text-center text-[11px] text-slate-500">
            NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
