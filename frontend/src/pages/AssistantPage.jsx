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
import './AssistantPage.css';

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

  const lines = content.split('\n');

  const renderInline = (text) => {
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
            className="judicial-citation-pill"
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
    <div className="judicial-text-wrapper">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-1" />;

        // Heading 3
        if (trimmed.startsWith('### ')) {
          return (
            <h3 key={idx} className="judicial-heading">
              {trimmed.replace('### ', '')}
            </h3>
          );
        }

        // Blockquote
        if (trimmed.startsWith('> ')) {
          return (
            <blockquote key={idx} className="judicial-blockquote">
              {renderInline(trimmed.replace(/^>\s*/, ''))}
            </blockquote>
          );
        }

        // Bullet list
        if (trimmed.startsWith('- ')) {
          return (
            <div key={idx} className="judicial-bullet-row">
              <span className="judicial-bullet-dot">•</span>
              <div className="flex-1">{renderInline(trimmed.replace(/^- \s*/, ''))}</div>
            </div>
          );
        }

        // Normal paragraph
        return <p key={idx} className="m-0">{renderInline(trimmed)}</p>;
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
      <div className="assistant-container">
        {/* Header (Panel 5 in Figma design) */}
        <div className="assistant-header">
          <div>
            <div className="assistant-title-group">
              <h1 className="assistant-title">
                Judicial AI Assistant
              </h1>
              <span className="assistant-badge-pill">
                Evidence-Grounded RAG
              </span>
            </div>
            <p className="assistant-subtitle">
              Ask questions about judicial cases, legal principles, statutory provisions, or specific Supreme Court judgments.
            </p>
          </div>
        </div>

        {/* Quick starter chips */}
        <div className="assistant-chips-container">
          <span className="assistant-chips-label">
            <Sparkles className="h-3 w-3 text-amber-500" />
            <span>Suggested:</span>
          </span>
          {QUICK_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              disabled={loading}
              onClick={() => handleSend(prompt)}
              className="assistant-chip-btn"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Conversation Stream */}
        <div className="assistant-chat-stream">
          {messages.map((msg, index) => {
            if (msg.role === 'user') {
              return (
                <div key={index} className="assistant-user-msg-row">
                  <div className="assistant-user-msg-bubble">
                    {msg.content}
                  </div>
                </div>
              );
            }

            // Assistant Message
            return (
              <div key={index} className="assistant-ai-msg-row">
                <div className="assistant-ai-avatar">
                  <Scale className="h-4 w-4 text-blue-400" />
                </div>

                <div className="assistant-ai-content-box">
                  <div className="assistant-ai-msg-card">
                    <FormattedJudicialText content={msg.content} />

                    {/* Insufficient Evidence Safeguard */}
                    {msg.hasSufficientEvidence === false && (
                      <div className="assistant-insufficient-warning">
                        <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                        <span>{msg.insufficientEvidenceReason || 'Insufficient judicial evidence found for this inquiry in the NYAYASETU repository.'}</span>
                      </div>
                    )}
                  </div>

                  {/* Expandable Evidence Container (Screen 5) */}
                  {msg.evidence && msg.evidence.length > 0 && (
                    <div className="assistant-evidence-drawer">
                      <button
                        type="button"
                        onClick={() => toggleEvidence(index)}
                        className="assistant-evidence-toggle-btn"
                      >
                        <span className="flex items-center gap-1.5">
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
                        <div className="assistant-evidence-list">
                          {msg.evidence.map((ev, evIdx) => (
                            <div key={evIdx} className="assistant-evidence-item">
                              <div className="assistant-evidence-card-top">
                                <div className="assistant-evidence-title-row">
                                  <div className="assistant-evidence-icon-box">
                                    <FileText className="h-3.5 w-3.5" />
                                  </div>
                                  <span className="assistant-evidence-title-text">
                                    {ev.citation_tag ? `${ev.citation_tag} ` : ''}
                                    {ev.case_title || ev.case_number || 'Supreme Court Record'}
                                  </span>
                                </div>
                                <div className="flex items-center gap-1.5 shrink-0">
                                  {ev.court_name && (
                                    <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-medium">
                                      {ev.court_name}
                                    </span>
                                  )}
                                  {ev.page_number && (
                                    <span className="assistant-evidence-page-pill">
                                      Page {ev.page_number}
                                    </span>
                                  )}
                                </div>
                              </div>

                              {ev.bench && (
                                <p className="assistant-evidence-coram">
                                  <span className="font-semibold text-slate-600">Coram:</span> {ev.bench}
                                </p>
                              )}

                              <p className="assistant-evidence-quote-box">
                                &ldquo;{ev.snippet}&rdquo;
                              </p>

                              <div className="assistant-evidence-links-row">
                                {ev.case_id ? (
                                  <Link
                                    to={`/cases/${ev.case_id}`}
                                    className="assistant-evidence-link-dossier"
                                  >
                                    <span>View Case Dossier</span>
                                    <ArrowRight className="h-3 w-3" />
                                  </Link>
                                ) : <div />}

                                <a
                                  href={ev.source_url || 'https://registry.opendata.aws/indian-supreme-court-judgments/'}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="assistant-evidence-link-source"
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
            <div className="flex items-start gap-3 py-2">
              <div className="assistant-ai-avatar">
                <Scale className="h-4 w-4 text-blue-400" />
              </div>
              <div className="assistant-loading-box">
                <div className="assistant-bounce-dot"></div>
                <div className="assistant-bounce-dot [animation-delay:0.2s]"></div>
                <div className="assistant-bounce-dot [animation-delay:0.4s]"></div>
                <span className="ml-2">Retrieving grounded judicial citations & synthesizing holding...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar & Disclaimer (Panel 5 in Figma design) */}
        <div className="assistant-input-bar-wrapper">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="assistant-input-form"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about cases, legal principles, or judgments..."
              className="assistant-chat-input"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="assistant-chat-submit"
              title="Send Message"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>

          {/* Legal Disclaimer matching Figma Panel 5 bottom */}
          <p className="assistant-bottom-disclaimer">
            NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
