import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { casesApi } from '../api/cases';
import AppLayout from '../components/AppLayout';
import {
  Calendar,
  AlertCircle,
  ArrowLeft
} from 'lucide-react';
import { TimelineSkeleton } from '../components/Skeleton';
import './TimelinePage.css';

export default function TimelinePage() {
  const { id } = useParams();
  const [timelineData, setTimelineData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchTimeline() {
      setLoading(true);
      setError(null);
      try {
        const data = await casesApi.getCaseTimeline(id);
        setTimelineData(data);
      } catch (err) {
        setError(err.message || 'Failed to load case timeline.');
      } finally {
        setLoading(false);
      }
    }
    fetchTimeline();
  }, [id]);

  if (loading) {
    return (
      <AppLayout>
        <div className="timeline-page-container">
          <div className="timeline-page-header">
            <Link to={`/cases/${id}`} className="timeline-back-link">
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Case Dossier</span>
            </Link>
            <h1 className="timeline-page-title">Case Procedural Timeline</h1>
            <p className="timeline-page-subtitle">Chronological record of judicial filings, hearings, and orders.</p>
          </div>
          <div style={{ marginTop: '2rem' }}>
            <TimelineSkeleton count={5} />
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error || !timelineData) {
    return (
      <AppLayout>
        <div className="timeline-page-container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto mb-3" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>Timeline Unavailable</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>{error || 'No chronological events recorded for this case.'}</p>
          <Link
            to={`/cases/${id}`}
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
            Return to Case Detail
          </Link>
        </div>
      </AppLayout>
    );
  }

  const { case_number, case_title, timeline } = timelineData;

  return (
    <AppLayout>
      <div className="timeline-page-container">
        {/* Breadcrumb Navigation */}
        <nav className="timeline-breadcrumb">
          <Link to="/search">Cases</Link>
          <span className="separator">&gt;</span>
          <Link to={`/cases/${id}`} style={{ maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {case_title || case_number}
          </Link>
          <span className="separator">&gt;</span>
          <span className="current">Timeline</span>
        </nav>

        {/* Header */}
        <div className="timeline-header-card">
          <div>
            <h1 className="timeline-title">Procedural Case Timeline</h1>
            <p className="timeline-subtitle">
              Chronological milestones from filing to final judgment for {case_number}.
            </p>
          </div>
          <Link
            to={`/cases/${id}`}
            className="timeline-btn-back"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Case Detail</span>
          </Link>
        </div>

        {/* Timeline Events Container */}
        <div className="timeline-card-wrapper">
          {timeline && timeline.length > 0 ? (
            <div className="timeline-flow-container">
              <div className="timeline-vertical-line" />
              {timeline.map((ev, i) => (
                <div key={i} className="timeline-event-card">
                  <div className="timeline-node-dot" />
                  <div className="timeline-event-date">
                    <Calendar className="h-3 w-3" />
                    <span>{ev.event_date}</span>
                  </div>
                  <h3 className="timeline-event-title">{ev.event_title || ev.event_type}</h3>
                  {ev.description && (
                    <p className="timeline-event-desc">{ev.description}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
              No procedural milestones recorded for this judgment.
            </p>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
