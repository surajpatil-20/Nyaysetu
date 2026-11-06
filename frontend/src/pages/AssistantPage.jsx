import { useState, useRef, useEffect } from 'react';
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
  HelpCircle
} from 'lucide-react';

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
        'In Pradeep v. State of Haryana (2023 INSC 599), the Supreme Court held that the testimony of a child witness can form the sole basis of conviction if it is found to be credible, trustworthy, and free from material contradictions. The Court reiterated that corroboration, though desirable, is not an absolute requirement.',
      evidenceCount: 5,
      evidence: [
        {
          case_title: 'Pradeep v. State of Haryana (2023 INSC 599)',
          page_number: 1,
          snippet:
            'testimony of child witness — Sole basis of conviction — When not proper — Appellant along with co-accused convicted under s. 302/34, IPC...',
          source_url:
            'https://indian-supreme-court-judgments.s3.amazonaws.com/2023/INSC_599.pdf',
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
        evidenceCount: (response.sources || response.evidence || []).length || 1,
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
            (err.message || 'Please try again.'),
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
      <div className="p-6 max-w-5xl mx-auto space-y-4 flex flex-col h-[calc(100vh-64px)]">
        {/* Header (Screen 5) */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Judicial AI Assistant
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Ask questions about judicial cases, legal principles, or specific judgments.
          </p>
        </div>

        {/* Conversation Stream (Screen 5) */}
        <div className="flex-1 bg-white border border-slate-200 rounded-xl p-5 overflow-y-auto space-y-6 shadow-xs">
          {messages.map((msg, index) => {
            if (msg.role === 'user') {
              return (
                <div key={index} className="flex justify-end">
                  <div className="bg-blue-100/90 text-slate-900 border border-blue-200/60 rounded-2xl rounded-tr-none px-4 py-3 max-w-xl text-xs sm:text-sm font-medium leading-relaxed shadow-2xs">
                    {msg.content}
                  </div>
                </div>
              );
            }

            // Assistant Message
            return (
              <div key={index} className="flex items-start space-x-3 max-w-2xl">
                <div className="h-8 w-8 rounded-full bg-[#0A192F] text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                  <Scale className="h-4 w-4 text-blue-400" />
                </div>

                <div className="space-y-3 flex-1">
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 shadow-2xs text-xs sm:text-sm text-slate-800 leading-relaxed">
                    <p className="whitespace-pre-wrap">{msg.content}</p>

                    {/* Insufficient Evidence Safeguard */}
                    {msg.hasSufficientEvidence === false && (
                      <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-start space-x-2">
                        <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
                        <span>{msg.insufficientEvidenceReason || 'Insufficient judicial evidence found for this inquiry.'}</span>
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
                          <span>Evidence ({msg.evidenceCount || msg.evidence.length})</span>
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
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-2">
                                  <div className="p-1 bg-rose-100 text-rose-600 rounded">
                                    <FileText className="h-3.5 w-3.5" />
                                  </div>
                                  <span className="font-bold text-slate-900">
                                    {ev.case_title || ev.case_number || 'Supreme Court Record'}
                                  </span>
                                </div>
                                {ev.page_number && (
                                  <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded text-[10px] font-medium">
                                    Page {ev.page_number}
                                  </span>
                                )}
                              </div>

                              <p className="text-slate-600 font-serif italic text-xs leading-relaxed bg-white p-2.5 rounded border border-slate-100">
                                &ldquo;{ev.snippet}&rdquo;
                              </p>

                              <div className="flex justify-end">
                                <a
                                  href={ev.source_url || 'https://registry.opendata.aws/indian-supreme-court-judgments/'}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-[11px] text-blue-600 hover:underline flex items-center space-x-1 font-semibold"
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
            <div className="flex items-center space-x-3 text-slate-500 text-xs py-2">
              <div className="h-8 w-8 rounded-full bg-[#0A192F] text-white flex items-center justify-center">
                <Scale className="h-4 w-4 text-blue-400" />
              </div>
              <div className="flex items-center space-x-1.5 bg-white border border-slate-200 rounded-xl px-4 py-2.5 shadow-2xs">
                <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce"></div>
                <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.2s]"></div>
                <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.4s]"></div>
                <span className="ml-2 text-slate-600">Retrieving grounded judicial citations...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar & Disclaimer (Screen 5) */}
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
              placeholder="Ask a question..."
              className="flex-1 px-4 py-3.5 text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white p-3.5 flex items-center justify-center transition disabled:opacity-50"
              title="Send Message"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>

          {/* Legal Disclaimer matching Screen 5 bottom */}
          <p className="text-center text-[11px] text-slate-500">
            NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
