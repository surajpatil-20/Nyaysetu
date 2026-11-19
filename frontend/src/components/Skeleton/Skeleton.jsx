import './Skeleton.css';

/**
 * Base atomic Skeleton component.
 * Accessible with role="status", aria-busy="true", aria-live="polite".
 */
export function Skeleton({
  width,
  height,
  variant = 'rect',
  className = '',
  style = {},
  ...props
}) {
  const variantClass = {
    text: 'ns-skeleton-rounded',
    title: 'ns-skeleton-rounded',
    rect: 'ns-skeleton-rounded',
    circle: 'ns-skeleton-circle',
    pill: 'ns-skeleton-pill',
  }[variant] || 'ns-skeleton-rounded';

  const defaultHeight = {
    text: '0.875rem',
    title: '1.5rem',
    rect: '100%',
    circle: width || '2.5rem',
    pill: '1.25rem',
  }[variant];

  return (
    <span
      role="status"
      aria-busy="true"
      aria-live="polite"
      className={`ns-skeleton ${variantClass} ${className}`}
      style={{
        width: width || '100%',
        height: height || defaultHeight,
        ...style,
      }}
      {...props}
    >
      <span className="sr-only">Loading judicial data...</span>
    </span>
  );
}

/**
 * Skeleton for Dashboard Page (Stats & Recent Cases)
 */
export function DashboardSkeleton() {
  return (
    <div className="skeleton-dashboard-wrapper" aria-busy="true" aria-live="polite">
      {/* 4 Stat Cards */}
      <div className="skeleton-dashboard-stats-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton-stat-card">
            <Skeleton variant="rect" width="2.75rem" height="2.75rem" style={{ borderRadius: 'var(--radius-md)' }} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <Skeleton variant="title" width="40%" height="1.5rem" />
              <Skeleton variant="text" width="70%" height="0.75rem" />
            </div>
          </div>
        ))}
      </div>

      {/* Recent Precedent Cases Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Skeleton variant="title" width="220px" height="1.5rem" />
          <Skeleton variant="pill" width="130px" height="1.25rem" />
        </div>

        <div className="skeleton-cases-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton-case-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <Skeleton variant="pill" width="90px" height="1.125rem" />
                  <Skeleton variant="title" width="90%" height="1.25rem" />
                </div>
                <Skeleton variant="circle" width="1.75rem" height="1.75rem" />
              </div>
              <Skeleton variant="text" width="96%" height="0.875rem" />
              <Skeleton variant="text" width="75%" height="0.875rem" />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
                <Skeleton variant="text" width="140px" height="0.75rem" />
                <Skeleton variant="pill" width="100px" height="1.25rem" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton for Search Results
 */
export function SearchSkeleton({ count = 5 }) {
  return (
    <div className="skeleton-search-results-list" aria-busy="true" aria-live="polite">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-search-card">
          {/* Top metadata row */}
          <div className="skeleton-search-top-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Skeleton variant="pill" width="110px" height="1.25rem" />
              <Skeleton variant="text" width="160px" height="0.75rem" />
            </div>
            <Skeleton variant="pill" width="85px" height="1.25rem" />
          </div>

          {/* Title */}
          <Skeleton variant="title" width="75%" height="1.375rem" />

          {/* Evidence snippet box */}
          <div className="skeleton-snippet-box">
            <Skeleton variant="text" width="98%" height="0.8125rem" />
            <Skeleton variant="text" width="92%" height="0.8125rem" />
            <Skeleton variant="text" width="60%" height="0.8125rem" />
          </div>

          {/* Actions & source row */}
          <div className="skeleton-search-actions">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Skeleton variant="pill" width="110px" height="1.5rem" />
              <Skeleton variant="pill" width="110px" height="1.5rem" />
            </div>
            <Skeleton variant="text" width="120px" height="0.75rem" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for Full Case Dossier Page
 */
export function CaseDossierSkeleton() {
  return (
    <div className="skeleton-dossier-wrapper" aria-busy="true" aria-live="polite">
      {/* Header Card */}
      <div className="skeleton-dossier-header-card">
        {/* Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Skeleton variant="text" width="70px" height="0.75rem" />
          <Skeleton variant="text" width="12px" height="0.75rem" />
          <Skeleton variant="text" width="180px" height="0.75rem" />
        </div>

        {/* Docket & Status */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <Skeleton variant="pill" width="120px" height="1.375rem" />
            <Skeleton variant="pill" width="80px" height="1.375rem" />
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Skeleton variant="pill" width="90px" height="1.75rem" />
            <Skeleton variant="pill" width="110px" height="1.75rem" />
          </div>
        </div>

        {/* Case Title */}
        <Skeleton variant="title" width="85%" height="2rem" />

        {/* Metadata row */}
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
          <Skeleton variant="text" width="180px" height="0.875rem" />
          <Skeleton variant="text" width="130px" height="0.875rem" />
          <Skeleton variant="text" width="160px" height="0.875rem" />
        </div>
      </div>

      {/* Tabs Row */}
      <div className="skeleton-dossier-tabs">
        {['Summary & Coram', 'Procedural Timeline', 'Knowledge Graph', 'Related Precedents', 'Judicial Documents'].map((_, idx) => (
          <Skeleton key={idx} variant="pill" width="130px" height="2rem" />
        ))}
      </div>

      {/* Body Grid */}
      <div className="skeleton-dossier-body-grid">
        {/* Left Column (Summary + Parties) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="skeleton-dossier-card">
            <Skeleton variant="title" width="180px" height="1.25rem" />
            <Skeleton variant="text" width="100%" height="0.875rem" />
            <Skeleton variant="text" width="97%" height="0.875rem" />
            <Skeleton variant="text" width="94%" height="0.875rem" />
            <Skeleton variant="text" width="85%" height="0.875rem" />
          </div>

          <div className="skeleton-dossier-card">
            <Skeleton variant="title" width="150px" height="1.25rem" />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ padding: '0.75rem', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                <Skeleton variant="text" width="80px" height="0.75rem" />
                <Skeleton variant="title" width="100%" height="1.125rem" style={{ marginTop: '0.375rem' }} />
              </div>
              <div style={{ padding: '0.75rem', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                <Skeleton variant="text" width="80px" height="0.75rem" />
                <Skeleton variant="title" width="100%" height="1.125rem" style={{ marginTop: '0.375rem' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (Bench & Official Documents) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="skeleton-dossier-card">
            <Skeleton variant="title" width="160px" height="1.25rem" />
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Skeleton variant="circle" width="2.5rem" height="2.5rem" />
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
                <Skeleton variant="text" width="70%" height="0.875rem" />
                <Skeleton variant="text" width="50%" height="0.75rem" />
              </div>
            </div>
          </div>

          <div className="skeleton-dossier-card">
            <Skeleton variant="title" width="140px" height="1.25rem" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                <Skeleton variant="text" width="60%" height="0.8125rem" />
                <Skeleton variant="pill" width="50px" height="1.25rem" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton for Case Timeline
 */
export function TimelineSkeleton({ count = 4 }) {
  return (
    <div className="skeleton-timeline-container" aria-busy="true" aria-live="polite">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-timeline-item">
          <div className="skeleton-timeline-dot" />
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <Skeleton variant="pill" width="85px" height="1.125rem" />
            <Skeleton variant="text" width="100px" height="0.75rem" />
          </div>
          <Skeleton variant="title" width="55%" height="1.125rem" />
          <Skeleton variant="text" width="90%" height="0.8125rem" />
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for Related Cases
 */
export function RelatedCasesSkeleton({ count = 4 }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }} aria-busy="true" aria-live="polite">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-case-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Skeleton variant="pill" width="100px" height="1.125rem" />
            <Skeleton variant="pill" width="80px" height="1.125rem" />
          </div>
          <Skeleton variant="title" width="85%" height="1.25rem" />
          <Skeleton variant="text" width="95%" height="0.8125rem" />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
            <Skeleton variant="text" width="120px" height="0.75rem" />
            <Skeleton variant="pill" width="90px" height="1.25rem" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for Knowledge Graph Canvas & Controls
 */
export function GraphSkeleton() {
  return (
    <div className="skeleton-graph-wrapper" aria-busy="true" aria-live="polite">
      <div className="skeleton-graph-viewport">
        <svg viewBox="0 0 760 480" className="skeleton-graph-wireframe">
          {/* Wireframe links */}
          <line x1="380" y1="240" x2="200" y2="130" stroke="var(--border-subtle)" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="380" y1="240" x2="560" y2="130" stroke="var(--border-subtle)" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="380" y1="240" x2="200" y2="350" stroke="var(--border-subtle)" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="380" y1="240" x2="560" y2="350" stroke="var(--border-subtle)" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="380" y1="240" x2="380" y2="90" stroke="var(--border-subtle)" strokeWidth="2" strokeDasharray="4 4" />

          {/* Wireframe outer nodes */}
          <circle cx="200" cy="130" r="24" fill="var(--skeleton-base)" />
          <circle cx="560" cy="130" r="24" fill="var(--skeleton-base)" />
          <circle cx="200" cy="350" r="24" fill="var(--skeleton-base)" />
          <circle cx="560" cy="350" r="24" fill="var(--skeleton-base)" />
          <circle cx="380" cy="90" r="20" fill="var(--skeleton-base)" />

          {/* Center case node */}
          <circle cx="380" cy="240" r="38" fill="var(--skeleton-base)" stroke="#ffffff" strokeWidth="4" />
        </svg>

        <div style={{ position: 'absolute', bottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-surface)', padding: '0.375rem 0.875rem', borderRadius: 'var(--radius-full)', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
          <div className="skeleton-ai-pulsing-dot" />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Synthesizing Knowledge Graph Ontology...</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton for AI Assistant message placeholder
 */
export function AIMessageSkeleton() {
  return (
    <div className="skeleton-ai-response-box" aria-busy="true" aria-live="polite">
      <Skeleton variant="circle" width="2rem" height="2rem" style={{ flexShrink: 0 }} />
      <div className="skeleton-ai-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--primary-navy)' }}>
            NYAYASETU AI
          </span>
          <div className="skeleton-ai-status-row">
            <span className="skeleton-ai-pulsing-dot" />
            <span>Analyzing available evidence...</span>
          </div>
        </div>

        <Skeleton variant="text" width="98%" height="0.875rem" />
        <Skeleton variant="text" width="94%" height="0.875rem" />
        <Skeleton variant="text" width="75%" height="0.875rem" />

        <div style={{ marginTop: '0.375rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <Skeleton variant="text" width="90%" height="0.875rem" />
          <Skeleton variant="text" width="55%" height="0.875rem" />
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton for Documents Repository List
 */
export function DocumentsSkeleton({ count = 4 }) {
  return (
    <div className="skeleton-docs-grid" aria-busy="true" aria-live="polite">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-doc-row">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
            <Skeleton variant="rect" width="2.5rem" height="2.5rem" style={{ borderRadius: 'var(--radius-md)', flexShrink: 0 }} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', flex: 1 }}>
              <Skeleton variant="title" width="60%" height="1.125rem" />
              <div style={{ display: 'flex', gap: '1rem' }}>
                <Skeleton variant="text" width="90px" height="0.75rem" />
                <Skeleton variant="text" width="60px" height="0.75rem" />
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Skeleton variant="pill" width="80px" height="1.25rem" />
            <Skeleton variant="pill" width="90px" height="1.75rem" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for Document Detail & Intelligence View
 */
export function DocumentDetailSkeleton() {
  return (
    <div className="skeleton-docdetail-grid" aria-busy="true" aria-live="polite">
      {/* Left PDF viewer canvas */}
      <div className="skeleton-pdf-viewer-box">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
          <Skeleton variant="title" width="180px" height="1.25rem" />
          <Skeleton variant="pill" width="90px" height="1.5rem" />
        </div>
        <Skeleton variant="rect" width="100%" height="450px" style={{ borderRadius: 'var(--radius-md)' }} />
      </div>

      {/* Right Document Intelligence Card */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div className="skeleton-dossier-card">
          <Skeleton variant="pill" width="100px" height="1.25rem" />
          <Skeleton variant="title" width="80%" height="1.5rem" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem', marginTop: '0.5rem' }}>
            <Skeleton variant="text" width="100%" height="0.875rem" />
            <Skeleton variant="text" width="95%" height="0.875rem" />
            <Skeleton variant="text" width="80%" height="0.875rem" />
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
            <Skeleton variant="pill" width="110px" height="2rem" />
            <Skeleton variant="pill" width="90px" height="2rem" />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton for Judicial Services Grid
 */
export function ServicesSkeleton({ count = 6 }) {
  return (
    <div className="skeleton-services-grid" aria-busy="true" aria-live="polite">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-service-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Skeleton variant="circle" width="2.5rem" height="2.5rem" />
            <Skeleton variant="pill" width="85px" height="1.125rem" />
          </div>
          <Skeleton variant="title" width="70%" height="1.25rem" />
          <Skeleton variant="text" width="95%" height="0.8125rem" />
          <Skeleton variant="text" width="85%" height="0.8125rem" />
          <div style={{ marginTop: '0.5rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
            <Skeleton variant="pill" width="110px" height="1.5rem" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for Admin Platform Metrics (ADMIN ONLY)
 */
export function AdminStatsSkeleton() {
  return (
    <div className="skeleton-admin-grid" aria-busy="true" aria-live="polite">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="skeleton-admin-card">
          <Skeleton variant="title" width="60px" height="2rem" />
          <Skeleton variant="text" width="90px" height="0.75rem" />
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for Citizen Profile Page
 */
export function ProfileSkeleton() {
  return (
    <div className="profile-card" aria-busy="true" aria-live="polite">
      <div className="profile-header-row">
        <div className="profile-user-left">
          <Skeleton variant="circle" width="4rem" height="4rem" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <Skeleton variant="title" width="180px" height="1.5rem" />
            <Skeleton variant="text" width="90px" height="0.875rem" />
          </div>
        </div>
        <Skeleton variant="pill" width="90px" height="1.5rem" />
      </div>

      <div className="profile-info-grid">
        <div className="profile-info-box">
          <Skeleton variant="text" width="80px" height="0.75rem" />
          <Skeleton variant="title" width="180px" height="1.125rem" style={{ marginTop: '0.375rem' }} />
        </div>
        <div className="profile-info-box">
          <Skeleton variant="text" width="110px" height="0.75rem" />
          <Skeleton variant="title" width="150px" height="1.125rem" style={{ marginTop: '0.375rem' }} />
        </div>
      </div>
    </div>
  );
}
