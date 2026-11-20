import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { lawsApi } from '../api/laws';
import AppLayout from '../components/AppLayout';
import {
  ArrowLeft,
  BookOpen,
  Scale,
  ExternalLink,
  PhoneCall,
  CheckCircle2,
  AlertCircle,
  FileText,
  Copy,
  Check,
  Building2,
  HelpCircle,
  ShieldCheck,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import './ScenarioDetailPage.css';

export default function ScenarioDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copiedSectionId, setCopiedSectionId] = useState(null);

  useEffect(() => {
    async function fetchDetail() {
      setLoading(true);
      setError(null);
      try {
        const data = await lawsApi.getScenarioDetail(id);
        setScenario(data);
      } catch (err) {
        console.error('Failed to load scenario details:', err);
        setError('Scenario not found or error loading legal provisions.');
      } finally {
        setLoading(false);
      }
    }
    fetchDetail();
  }, [id]);

  const handleCopyLink = (secId, url) => {
    navigator.clipboard.writeText(url);
    setCopiedSectionId(secId);
    setTimeout(() => setCopiedSectionId(null), 2000);
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="sd-page-container">
          <div className="sd-skeleton-header">
            <div className="sd-skeleton-line short" />
            <div className="sd-skeleton-line title" />
            <div className="sd-skeleton-line text" />
          </div>
          <div className="sd-skeleton-card" />
          <div className="sd-skeleton-card" />
        </div>
      </AppLayout>
    );
  }

  if (error || !scenario) {
    return (
      <AppLayout>
        <div className="sd-page-container">
          <div className="sd-error-card">
            <AlertCircle className="h-10 w-10 text-red-500 mb-2" />
            <h2 className="text-base font-bold text-[var(--text-primary)]">Legal Scenario Not Found</h2>
            <p className="text-xs text-[var(--text-muted)] max-w-sm mt-1">
              {error || 'The requested real-life legal situation could not be located in our verified dataset.'}
            </p>
            <Link to="/know-your-law" className="mt-4 sd-back-btn">
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Know Your Law</span>
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  // Parse what_to_do bullet points or steps
  const steps = scenario.what_to_do
    ? scenario.what_to_do.split('\n').filter((s) => s.trim().length > 0)
    : [];

  return (
    <AppLayout>
      <div className="sd-page-container">
        {/* Breadcrumb Navigation */}
        <nav className="sd-breadcrumb-nav" aria-label="Breadcrumb">
          <Link to="/know-your-law" className="sd-breadcrumb-link">
            Know Your Law
          </Link>
          <ChevronRight className="h-3.5 w-3.5 text-[var(--text-muted)]" />
          <span className="sd-breadcrumb-current">
            {scenario.category?.name || 'Scenario'}
          </span>
          <ChevronRight className="h-3.5 w-3.5 text-[var(--text-muted)]" />
          <span className="sd-breadcrumb-title truncate max-w-xs">
            {scenario.title}
          </span>
        </nav>

        {/* Back Link */}
        <div>
          <button
            type="button"
            onClick={() => navigate('/know-your-law')}
            className="sd-back-btn"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to All Situations</span>
          </button>
        </div>

        {/* Header Hero */}
        <header className="sd-hero-card">
          <div className="sd-hero-top-row">
            <span className="sd-category-pill">
              {scenario.category?.name}
            </span>
            <span className="sd-verified-badge">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
              <span>India Code Verified</span>
            </span>
          </div>

          <h1 className="sd-hero-title">{scenario.title}</h1>

          {/* Quick Action Bar: Portal & Helpline */}
          <div className="sd-action-bar">
            {scenario.helpline_number && (
              <div className="sd-helpline-box">
                <PhoneCall className="h-4 w-4 text-emerald-600" />
                <div>
                  <span className="sd-helpline-tag">Official Citizen Helpline:</span>
                  <span className="sd-helpline-value">{scenario.helpline_number}</span>
                </div>
              </div>
            )}

            {scenario.official_portal_url && (
              <a
                href={scenario.official_portal_url}
                target="_blank"
                rel="noopener noreferrer"
                className="sd-portal-btn"
              >
                <span>Launch Grievance / e-Filing Portal</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            )}
          </div>
        </header>

        {/* Real-Life Situation Card */}
        <section className="sd-section-card" aria-labelledby="situation-heading">
          <div className="sd-section-header">
            <HelpCircle className="h-5 w-5 text-[#FFA425]" />
            <h2 id="situation-heading" className="sd-section-title">
              The Real-Life Situation
            </h2>
          </div>
          <p className="sd-situation-text">
            {scenario.situation_summary}
          </p>
        </section>

        {/* What You Should Do Action Steps */}
        <section className="sd-section-card" aria-labelledby="actions-heading">
          <div className="sd-section-header">
            <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            <h2 id="actions-heading" className="sd-section-title">
              What You Should Do (Actionable Citizen Steps)
            </h2>
          </div>

          <div className="sd-steps-list">
            {steps.map((step, idx) => (
              <div key={idx} className="sd-step-item">
                <span className="sd-step-number">{idx + 1}</span>
                <div className="sd-step-content">
                  <p className="sd-step-text">{step.replace(/^\d+\.\s*/, '')}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Relevant Acts & Statutory Sections */}
        <section className="sd-law-sections-wrap" aria-labelledby="laws-heading">
          <div className="sd-section-header">
            <Scale className="h-5 w-5 text-[#11486B]" />
            <div>
              <h2 id="laws-heading" className="sd-section-title">
                Applicable Indian Laws &amp; Statutory Sections
              </h2>
              <p className="sd-section-subtitle">
                Authoritative enactments of the Parliament of India governing this scenario, verified from the India Code legislative repository.
              </p>
            </div>
          </div>

          <div className="sd-sections-grid">
            {scenario.sections && scenario.sections.length > 0 ? (
              scenario.sections.map((sec) => {
                const isCopied = copiedSectionId === sec.id;

                return (
                  <article key={sec.id} className="sd-law-card" aria-labelledby={`sec-title-${sec.id}`}>
                    <div className="sd-law-card-header">
                      <div>
                        <span className="sd-act-badge">
                          {sec.act?.short_code || sec.act?.act_name} ({sec.act?.act_year})
                        </span>
                        <h3 id={`sec-title-${sec.id}`} className="sd-sec-title">
                          {sec.section_number}: {sec.title}
                        </h3>
                        <p className="sd-act-full-name">
                          {sec.act?.act_name}
                        </p>
                      </div>

                      <div className="sd-law-card-actions">
                        <button
                          type="button"
                          onClick={() => handleCopyLink(sec.id, sec.official_url)}
                          className="sd-copy-link-btn"
                          title="Copy official India Code link"
                        >
                          {isCopied ? (
                            <>
                              <Check className="h-3 w-3 text-emerald-600" />
                              <span className="text-emerald-600 text-xs">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3 w-3" />
                              <span className="text-xs">Copy Link</span>
                            </>
                          )}
                        </button>

                        <a
                          href={sec.official_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="sd-india-code-btn"
                          title="Open official section on India Code"
                        >
                          <span>India Code Source</span>
                          <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                      </div>
                    </div>

                    {/* Simple Citizen Explanation (Prominently Highlighted) */}
                    <div className="sd-explanation-box">
                      <div className="flex items-start gap-2">
                        <Sparkles className="h-4 w-4 text-[#FFA425] shrink-0 mt-0.5" />
                        <div>
                          <h4 className="sd-box-heading">Plain-Language Citizen Meaning</h4>
                          <p className="sd-explanation-text">
                            {sec.simple_explanation}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Statutory Provision Text */}
                    <div className="sd-statute-text-box">
                      <h4 className="sd-box-heading">Official Statutory Text (India Code)</h4>
                      <blockquote className="sd-statute-quote">
                        &ldquo;{sec.legal_text}&rdquo;
                      </blockquote>
                    </div>

                    {/* Punishment or Statutory Remedy */}
                    {sec.punishment_or_remedy && (
                      <div className="sd-remedy-box">
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="sd-box-heading text-emerald-800">
                              Statutory Remedy / Punishment
                            </h4>
                            <p className="sd-remedy-text">
                              {sec.punishment_or_remedy}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </article>
                );
              })
            ) : (
              <div className="sd-empty-sections">
                <p>No specific statutory sections linked to this scenario yet.</p>
              </div>
            )}
          </div>
        </section>

        {/* Civic Information Disclaimer */}
        <footer className="sd-disclaimer-box">
          <div className="flex items-start gap-2.5">
            <Scale className="h-4 w-4 text-[#FFA425] shrink-0 mt-0.5" />
            <div className="text-xs text-[var(--text-muted)] leading-relaxed">
              <strong className="text-[var(--text-primary)]">Civic Judicial Awareness Notice: </strong>
              This information is published to enhance public legal literacy in accordance with official India Code statutes. 
              It does not constitute formal legal representation, advocacy, or an attorney-client relationship. If you are facing litigation or criminal charges, always consult an enrolled advocate or seek free legal aid from your local DLSA (District Legal Services Authority) via helpline 15100.
            </div>
          </div>
        </footer>
      </div>
    </AppLayout>
  );
}
