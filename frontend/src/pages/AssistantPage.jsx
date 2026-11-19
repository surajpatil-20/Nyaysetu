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
  ArrowRight
} from 'lucide-react';
import './AssistantPage.css';

const QUICK_PROMPTS = [
  'Principles of natural justice in S. Narahari v S.R. Kumar',
  'Motor accident third-party compensation in T.J. Parameshwarappa',
  'Standard of proof in criminal appeals in Union of India v Munshi Ram',
  'Taxation principles in Santhosh Maize v State of Tamil Nadu',
  'Child witness testimony in Pradeep v State of Haryana',
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
        return <strong key={i} className="judicial-text-bold">{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="judicial-text-wrapper">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="judicial-spacer" />;

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
              <div className="judicial-bullet-text">{renderInline(trimmed.replace(/^- \s*/, ''))}</div>
            </div>
          );
        }

        // Normal paragraph
        return <p key={idx} className="judicial-paragraph">{renderInline(trimmed)}</p>;
      })}
    </div>
  );
}

export default function AssistantPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        '### Welcome to NYAYASETU Evidence-Grounded Legal Research\nI am your judicial research assistant, grounded across **105 Supreme Court precedents** and **2,058 indexed document chunks**.\n\nYou can ask inquiries regarding any case in our repository (e.g. natural justice in *S. Narahari*, motor accident claims in *T.J. Parameshwarappa*, tax disputes in *Santhosh Maize*, or criminal appeals in *Union of India v. Munshi Ram*).\n\nSelect a suggested topic above or type your inquiry below.',
      evidenceCount: 0,
      evidence: [],
      showEvidence: false,
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

      const rawEvidence = response.sources || response.evidence || [];
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        hasSufficientEvidence: response.has_sufficient_evidence ?? true,
        insufficientEvidenceReason: response.insufficient_evidence_reason,
        evidence: rawEvidence,
        evidenceCount: rawEvidence.length || 0,
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
        {/* Header */}
        <div className="assistant-header">
          <div>
            <div className="assistant-title-group">
              <h1 className="assistant-title">Judicial AI Assistant</h1>
              <span className="assistant-badge-pill">Evidence Grounded</span>
            </div>
            <p className="assistant-subtitle">
              Ask questions about judicial cases, legal principles, or specific precedents across India's Supreme Court jurisprudence.
            </p>
          </div>
        </div>

        {/* Suggested Question Chips */}
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
                  <Scale className="h-4 w-4" />
                </div>

                <div className="assistant-ai-content-box">
                  <div className="assistant-ai-msg-card">
                    <FormattedJudicialText content={msg.content} />

                    {/* Insufficient Evidence Safeguard */}
                    {msg.hasSufficientEvidence === false && (
                      <div className="assistant-insufficient-warning">
                        <AlertCircle className="h-4 w-4 shrink-0" />
                        <span>{msg.insufficientEvidenceReason || 'Insufficient judicial evidence found for this inquiry in the NYAYASETU repository.'}</span>
                      </div>
                    )}
                  </div>

                  {/* Expandable Evidence Card */}
                  {msg.evidence && msg.evidence.length > 0 && (
                    <div className="assistant-evidence-drawer">
                      <button
                        type="button"
                        onClick={() => toggleEvidence(index)}
                        className="assistant-evidence-toggle-btn"
                      >
                        <span className="assistant-evidence-toggle-label">
                          <span>Evidence ({msg.evidenceCount || msg.evidence.length})</span>
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
                                    <FileText className="h-4 w-4" />
                                  </div>
                                  <span className="assistant-evidence-title-text">
                                    {ev.case_title || ev.case_number || 'Supreme Court Precedent'}
                                  </span>
                                </div>
                                <div className="assistant-evidence-tags">
                                  <span className="assistant-evidence-page-pill">
                                    Page {ev.page_number || 1}
                                  </span>
                                </div>
                              </div>

                              <p className="assistant-evidence-quote-box">
                                {ev.snippet || '...grounded quotation extracted from judgment record...'}
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
                                  href={ev.source_url || 'https://indian-supreme-court-judgments.s3.amazonaws.com/'}
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
            <div className="assistant-ai-msg-row">
              <div className="assistant-ai-avatar">
                <Scale className="h-4 w-4" />
              </div>
              <div className="assistant-loading-box">
                <div className="assistant-bounce-dot"></div>
                <div className="assistant-bounce-dot bounce-2"></div>
                <div className="assistant-bounce-dot bounce-3"></div>
                <span className="assistant-loading-text">Synthesizing evidence-grounded judicial holding across 105 precedents...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar & Disclaimer */}
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
              placeholder="Ask a question about any precedent, legal doctrine, or statutory section..."
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

          {/* Legal Disclaimer */}
          <p className="assistant-bottom-disclaimer">
            NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
